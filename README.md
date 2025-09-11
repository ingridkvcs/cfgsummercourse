package main

import (
	"encoding/base64"
	"encoding/json"
	"testing"

	corev1 "github.com/kubewarden/k8s-objects/api/core/v1"
	metav1 "github.com/kubewarden/k8s-objects/apimachinery/pkg/apis/meta/v1"
	mocks "github.com/kubewarden/policy-sdk-go/pkg/capabilities/mocks"
	kubewarden_protocol "github.com/kubewarden/policy-sdk-go/protocol"
	kubewarden_testing "github.com/kubewarden/policy-sdk-go/testing"
	"github.com/stretchr/testify/mock"
)

func TestAllowedAppsAreNotMutated(t *testing.T) {
	// Test that pods belonging to allowed apps (non-DaemonSet) are accepted without mutation
	// DaemonSet testing is covered by TestDaemonSetPodsAreNotMutated

	testCases := []struct {
		name        string
		pod         corev1.Pod
		settings    Settings
		shouldPass  bool
		description string
	}{
		{
			name: "Deployment pod should not be mutated when allowed",
			pod: corev1.Pod{
				Metadata: &metav1.ObjectMeta{
					Name:      "nginx-deployment-78abc",
					Namespace: "production",
					OwnerReferences: []*metav1.OwnerReference{
						{
							Kind: func() *string { s := "ReplicaSet"; return &s }(),
							Name: func() *string { s := "nginx-deployment-5c8b9"; return &s }(),
						},
					},
				},
				Spec: &corev1.PodSpec{},
			},
			settings: Settings{
				WorkloadTolerationKey: "workload",
				WorkloadNamespaceTag:  "Workload",
				AllowedApps: []AllowedApp{
					{Kind: "Deployment", Name: "nginx-deployment", Namespace: "production"},
				},
			},
			shouldPass:  true,
			description: "Deployment pods should be accepted without mutations when allowed",
		},
		{
			name: "StatefulSet pod should not be mutated when allowed",
			pod: corev1.Pod{
				Metadata: &metav1.ObjectMeta{
					Name:      "postgres-0",
					Namespace: "database",
					OwnerReferences: []*metav1.OwnerReference{
						{
							Kind: func() *string { s := "StatefulSet"; return &s }(),
							Name: func() *string { s := "postgres"; return &s }(),
						},
					},
				},
				Spec: &corev1.PodSpec{
					Tolerations: []*corev1.Toleration{
						{Key: "dedicated", Operator: "Equal", Value: "database", Effect: "NoSchedule"},
					},
				},
			},
			settings: Settings{
				WorkloadTolerationKey: "workload",
				WorkloadNamespaceTag:  "Workload",
				AllowedApps: []AllowedApp{
					{Kind: "StatefulSet", Name: "postgres", Namespace: "database"},
				},
			},
			shouldPass:  true,
			description: "StatefulSet pods should be accepted without mutations when allowed",
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			// Reset host client to ensure clean test state
			host.Client = nil

			// Build the validation request
			payload, err := kubewarden_testing.BuildValidationRequest(&tc.pod, &tc.settings)
			if err != nil {
				t.Fatalf("Failed to build validation request: %v", err)
			}

			// Execute mutation
			responsePayload, err := validate(payload)
			if err != nil {
				t.Fatalf("Mutation failed with error: %v", err)
			}

			// Parse response
			var response kubewarden_protocol.ValidationResponse
			if err := json.Unmarshal(responsePayload, &response); err != nil {
				t.Fatalf("Failed to unmarshal response: %v", err)
			}

			// Check acceptance
			if tc.shouldPass && !response.Accepted {
				t.Errorf("%s: Expected pod to be accepted, but it was rejected. Message: %v",
					tc.description, response.Message)
			}
			if !tc.shouldPass && response.Accepted {
				t.Errorf("%s: Expected pod to be rejected, but it was accepted", tc.description)
			}

			// For allowed apps, verify no mutation occurred
			if tc.shouldPass && response.MutatedObject != nil {
				t.Errorf("%s: Expected no mutation for allowed app, but mutation occurred", tc.description)
			}
		})
	}
}


func TestPodNoMutationWhenNamespaceHasNoWorkloadAnnotation(t *testing.T) {
	// Test 1: Pod should not get toleration when namespace has no Workload annotation
	settings := Settings{
		WorkloadTolerationKey: "workload",
		WorkloadNamespaceTag:  "Workload",
		AllowedApps:           []AllowedApp{},
	}

	pod := corev1.Pod{
		Metadata: &metav1.ObjectMeta{
			Name:      "test-pod",
			Namespace: "test-namespace",
		},
		Spec: &corev1.PodSpec{
			Tolerations: nil,
		},
	}

	// Create namespace WITHOUT workload annotation
	namespace := corev1.Namespace{
		Metadata: &metav1.ObjectMeta{
			Name:        "test-namespace",
			Annotations: map[string]string{
				// No "Workload" annotation
				"other-annotation": "some-value",
			},
		},
	}

	// Setup mock
	mockClient := &mocks.MockWapcClient{}
	namespaceRaw, _ := json.Marshal(namespace)
	mockClient.On("HostCall", "kubewarden", "kubernetes", "get_resource", mock.Anything).Return(namespaceRaw, nil)
	host.Client = mockClient
	defer func() { host.Client = nil }()

	// Execute validation
	payload, _ := kubewarden_testing.BuildValidationRequest(&pod, &settings)
	responsePayload, err := validate(payload)
	if err != nil {
		t.Fatalf("Validation failed: %v", err)
	}

	// Parse response
	var response kubewarden_protocol.ValidationResponse
	json.Unmarshal(responsePayload, &response)

	if !response.Accepted {
		t.Fatalf("Pod should be accepted: %v", response.Message)
	}

	// Verify NO mutation occurred
	if response.MutatedObject != nil {
		t.Errorf("Expected no mutation when namespace has no Workload annotation, but mutation occurred")
	}
}

func TestPodGetsSingleTolerationFromNamespace(t *testing.T) {
	// Test 2 & 3: Pod should get exactly one toleration from namespace annotation
	settings := Settings{
		WorkloadTolerationKey: "workload",
		WorkloadNamespaceTag:  "Workload",
		AllowedApps:           []AllowedApp{},
	}

	pod := corev1.Pod{
		Metadata: &metav1.ObjectMeta{
			Name:      "test-pod",
			Namespace: "test-namespace",
		},
		Spec: &corev1.PodSpec{
			Tolerations: nil,
		},
	}

	// Create namespace WITH workload annotation
	namespace := corev1.Namespace{
		Metadata: &metav1.ObjectMeta{
			Name: "test-namespace",
			Annotations: map[string]string{
				"Workload": "backend",
			},
		},
	}

	// Setup mock
	mockClient := &mocks.MockWapcClient{}
	namespaceRaw, _ := json.Marshal(namespace)
	mockClient.On("HostCall", "kubewarden", "kubernetes", "get_resource", mock.Anything).Return(namespaceRaw, nil)
	host.Client = mockClient
	defer func() { host.Client = nil }()

	// Execute validation
	payload, _ := kubewarden_testing.BuildValidationRequest(&pod, &settings)
	responsePayload, err := validate(payload)
	if err != nil {
		t.Fatalf("Validation failed: %v", err)
	}

	// Parse response
	var response kubewarden_protocol.ValidationResponse
	json.Unmarshal(responsePayload, &response)

	if !response.Accepted {
		t.Fatalf("Pod should be accepted: %v", response.Message)
	}

	// Verify mutation occurred
	if response.MutatedObject == nil {
		t.Fatal("Expected mutation when namespace has Workload annotation")
	}

	// Parse mutated pod
	var mutatedPod corev1.Pod
	mutatedBase64 := response.MutatedObject.(string)
	mutatedBytes, _ := base64.StdEncoding.DecodeString(mutatedBase64)
	json.Unmarshal(mutatedBytes, &mutatedPod)

	// Verify exactly ONE toleration was added
	if len(mutatedPod.Spec.Tolerations) != 1 {
		t.Errorf("Expected exactly 1 toleration, got %d", len(mutatedPod.Spec.Tolerations))
	}

	// Verify the toleration is correct
	if len(mutatedPod.Spec.Tolerations) > 0 {
		tol := mutatedPod.Spec.Tolerations[0]
		if tol.Key != "workload" || tol.Value != "backend" || tol.Operator != "Equal" || tol.Effect != "NoExecute" {
			t.Errorf("Toleration has incorrect values: %+v", tol)
		}
	}
}

func TestPodWithExistingTolerationGetsOnlyOne(t *testing.T) {
	// Test 4: Pod with existing workload toleration should only have one (replaced, not added)
	settings := Settings{
		WorkloadTolerationKey: "workload",
		WorkloadNamespaceTag:  "Workload",
		AllowedApps:           []AllowedApp{},
	}

	pod := corev1.Pod{
		Metadata: &metav1.ObjectMeta{
			Name:      "test-pod",
			Namespace: "test-namespace",
		},
		Spec: &corev1.PodSpec{
			Tolerations: []*corev1.Toleration{
				{Key: "workload", Operator: "Equal", Value: "old-value", Effect: "NoExecute"},
				{Key: "other-key", Operator: "Equal", Value: "other-value", Effect: "NoSchedule"},
			},
		},
	}

	// Create namespace with workload annotation
	namespace := corev1.Namespace{
		Metadata: &metav1.ObjectMeta{
			Name: "test-namespace",
			Annotations: map[string]string{
				"Workload": "new-backend",
			},
		},
	}

	// Setup mock
	mockClient := &mocks.MockWapcClient{}
	namespaceRaw, _ := json.Marshal(namespace)
	mockClient.On("HostCall", "kubewarden", "kubernetes", "get_resource", mock.Anything).Return(namespaceRaw, nil)
	host.Client = mockClient
	defer func() { host.Client = nil }()

	// Execute validation
	payload, _ := kubewarden_testing.BuildValidationRequest(&pod, &settings)
	responsePayload, err := validate(payload)
	if err != nil {
		t.Fatalf("Validation failed: %v", err)
	}

	// Parse response
	var response kubewarden_protocol.ValidationResponse
	json.Unmarshal(responsePayload, &response)

	if !response.Accepted {
		t.Fatalf("Pod should be accepted: %v", response.Message)
	}

	// Verify mutation occurred
	if response.MutatedObject == nil {
		t.Fatal("Expected mutation to replace existing workload toleration")
	}

	// Parse mutated pod
	var mutatedPod corev1.Pod
	mutatedBase64 := response.MutatedObject.(string)
	mutatedBytes, _ := base64.StdEncoding.DecodeString(mutatedBase64)
	json.Unmarshal(mutatedBytes, &mutatedPod)

	// Verify still 2 tolerations (one replaced, one kept)
	if len(mutatedPod.Spec.Tolerations) != 2 {
		t.Errorf("Expected 2 tolerations (1 workload + 1 other), got %d", len(mutatedPod.Spec.Tolerations))
	}

	// Count workload tolerations
	workloadCount := 0
	for _, tol := range mutatedPod.Spec.Tolerations {
		if tol.Key == "workload" {
			workloadCount++
			// Verify it has the new value
			if tol.Value != "new-backend" {
				t.Errorf("Workload toleration should have new value 'new-backend', got '%s'", tol.Value)
			}
		}
	}

	if workloadCount != 1 {
		t.Errorf("Expected exactly 1 workload toleration, found %d", workloadCount)
	}
}

func TestDaemonSetPodsAreNotMutated(t *testing.T) {
	// Test 5: DaemonSet pods should not get tolerations added
	settings := Settings{
		WorkloadTolerationKey: "workload",
		WorkloadNamespaceTag:  "Workload",
		AllowedApps: []AllowedApp{
			{Kind: "DaemonSet", Name: "test-daemonset", Namespace: "test-namespace"},
		},
	}

	pod := corev1.Pod{
		Metadata: &metav1.ObjectMeta{
			Name:      "test-daemonset-pod",
			Namespace: "test-namespace",
			OwnerReferences: []*metav1.OwnerReference{
				{
					Kind: func() *string { s := "DaemonSet"; return &s }(),
					Name: func() *string { s := "test-daemonset"; return &s }(),
				},
			},
		},
		Spec: &corev1.PodSpec{
			Tolerations: nil,
		},
	}

	// Create namespace WITH workload annotation (should be ignored for DaemonSet)
	namespace := corev1.Namespace{
		Metadata: &metav1.ObjectMeta{
			Name: "test-namespace",
			Annotations: map[string]string{
				"Workload": "should-be-ignored",
			},
		},
	}

	// Setup mock
	mockClient := &mocks.MockWapcClient{}
	namespaceRaw, _ := json.Marshal(namespace)
	mockClient.On("HostCall", "kubewarden", "kubernetes", "get_resource", mock.Anything).Return(namespaceRaw, nil)
	host.Client = mockClient
	defer func() { host.Client = nil }()

	// Execute validation
	payload, _ := kubewarden_testing.BuildValidationRequest(&pod, &settings)
	responsePayload, err := validate(payload)
	if err != nil {
		t.Fatalf("Validation failed: %v", err)
	}

	// Parse response
	var response kubewarden_protocol.ValidationResponse
	json.Unmarshal(responsePayload, &response)

	if !response.Accepted {
		t.Fatalf("DaemonSet pod should be accepted: %v", response.Message)
	}

	// Verify NO mutation occurred for DaemonSet
	if response.MutatedObject != nil {
		t.Errorf("DaemonSet pods should not be mutated, but mutation occurred")
	}
}

func TestPodNoMutationWhenNamespaceHasNoWorkloadAnnotation(t *testing.T) {
	// Test 1: Pod should not get toleration when namespace has no Workload annotation
	settings := Settings{
		WorkloadTolerationKey: "workload",
		WorkloadNamespaceTag:  "Workload",
		AllowedApps:           []AllowedApp{},
	}

	pod := corev1.Pod{
		Metadata: &metav1.ObjectMeta{
			Name:      "test-pod",
			Namespace: "test-namespace",
		},
		Spec: &corev1.PodSpec{
			Tolerations: nil,
		},
	}

	// Create namespace WITHOUT workload annotation
	namespace := corev1.Namespace{
		Metadata: &metav1.ObjectMeta{
			Name: "test-namespace",
			Annotations: map[string]string{
				// No "Workload" annotation
				"other-annotation": "some-value",
			},
		},
	}

	// Setup mock
	mockClient := &mocks.MockWapcClient{}
	namespaceRaw, _ := json.Marshal(namespace)
	mockClient.On("HostCall", "kubewarden", "kubernetes", "get_resource", mock.Anything).Return(namespaceRaw, nil)
	host.Client = mockClient
	defer func() { host.Client = nil }()

	// Execute validation
	payload, _ := kubewarden_testing.BuildValidationRequest(&pod, &settings)
	responsePayload, err := validate(payload)
	if err != nil {
		t.Fatalf("Validation failed: %v", err)
	}

	// Parse response
	var response kubewarden_protocol.ValidationResponse
	json.Unmarshal(responsePayload, &response)

	if !response.Accepted {
		t.Fatalf("Pod should be accepted: %v", response.Message)
	}

	// Verify NO mutation occurred
	if response.MutatedObject != nil {
		t.Errorf("Expected no mutation when namespace has no Workload annotation, but mutation occurred")
	}
}
