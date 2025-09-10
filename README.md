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
	// Test that pods belonging to allowed apps are accepted without mutation

	testCases := []struct {
		name        string
		pod         corev1.Pod
		settings    Settings
		shouldPass  bool
		description string
	}{
		{
			name: "Cilium DaemonSet pod should not be mutated",
			pod: corev1.Pod{
				Metadata: &metav1.ObjectMeta{
					Name:      "cilium-agent-xyz",
					Namespace: "kube-system",
					OwnerReferences: []*metav1.OwnerReference{
						{
							Kind: func() *string { s := "DaemonSet"; return &s }(),
							Name: func() *string { s := "cilium"; return &s }(),
						},
					},
				},
				Spec: &corev1.PodSpec{
					// Even if it has existing tolerations, they shouldn't be touched
					Tolerations: []*corev1.Toleration{
						{
							Key:      "workload",
							Operator: "Equal",
							Value:    "existing-value",
							Effect:   "NoExecute",
						},
					},
				},
			},
			settings: Settings{
				WorkloadTolerationKey: "workload",
				WorkloadNamespaceTag:  "Workload",
				AllowedApps: []AllowedApp{
					{Kind: "DaemonSet", Name: "cilium", Namespace: "kube-system"},
				},
			},
			shouldPass:  true,
			description: "Cilium DaemonSet pods should be accepted without any mutations",
		},
		{
			name: "CSI node DaemonSet should not be mutated",
			pod: corev1.Pod{
				Metadata: &metav1.ObjectMeta{
					Name:      "csi-nfs-node-abc",
					Namespace: "kube-system",
					OwnerReferences: []*metav1.OwnerReference{
						{
							Kind: func() *string { s := "DaemonSet"; return &s }(),
							Name: func() *string { s := "csi-nfs-node"; return &s }(),
						},
					},
				},
				Spec: &corev1.PodSpec{},
			},
			settings: Settings{
				WorkloadTolerationKey: "workload",
				WorkloadNamespaceTag:  "Workload",
				AllowedApps: []AllowedApp{
					{Kind: "DaemonSet", Name: "csi-nfs-node", Namespace: "kube-system"},
				},
			},
			shouldPass:  true,
			description: "CSI node DaemonSet should be accepted without mutations",
		},
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
		{
			name: "Pod with multiple owner references should match correctly",
			pod: corev1.Pod{
				Metadata: &metav1.ObjectMeta{
					Name:      "job-pod-xyz",
					Namespace: "kube-system",
					OwnerReferences: []*metav1.OwnerReference{
						{
							Kind: func() *string { s := "Job"; return &s }(),
							Name: func() *string { s := "backup-job"; return &s }(),
						},
						{
							Kind: func() *string { s := "DaemonSet"; return &s }(),
							Name: func() *string { s := "node-exporter"; return &s }(),
						},
					},
				},
				Spec: &corev1.PodSpec{},
			},
			settings: Settings{
				WorkloadTolerationKey: "workload",
				WorkloadNamespaceTag:  "Workload",
				AllowedApps: []AllowedApp{
					{Kind: "DaemonSet", Name: "node-exporter", Namespace: "kube-system"},
				},
			},
			shouldPass:  true,
			description: "Pod with multiple owners should match if any owner is allowed",
		},
		{
			name: "Wrong namespace should still get mutated",
			pod: corev1.Pod{
				Metadata: &metav1.ObjectMeta{
					Name:      "cilium-agent-xyz",
					Namespace: "default", // Wrong namespace
					OwnerReferences: []*metav1.OwnerReference{
						{
							Kind: func() *string { s := "DaemonSet"; return &s }(),
							Name: func() *string { s := "cilium"; return &s }(),
						},
					},
				},
				Spec: &corev1.PodSpec{},
			},
			settings: Settings{
				WorkloadTolerationKey: "workload",
				WorkloadNamespaceTag:  "Workload",
				AllowedApps: []AllowedApp{
					{Kind: "DaemonSet", Name: "cilium", Namespace: "kube-system"},
				},
			},
			shouldPass:  false, // Should get mutated, not exempted
			description: "Pod in wrong namespace should not be exempted",
		},
		{
			name: "Wrong name should still get mutated",
			pod: corev1.Pod{
				Metadata: &metav1.ObjectMeta{
					Name:      "other-agent-xyz",
					Namespace: "kube-system",
					OwnerReferences: []*metav1.OwnerReference{
						{
							Kind: func() *string { s := "DaemonSet"; return &s }(),
							Name: func() *string { s := "other-agent"; return &s }(), // Wrong name
						},
					},
				},
				Spec: &corev1.PodSpec{},
			},
			settings: Settings{
				WorkloadTolerationKey: "workload",
				WorkloadNamespaceTag:  "Workload",
				AllowedApps: []AllowedApp{
					{Kind: "DaemonSet", Name: "cilium", Namespace: "kube-system"},
				},
			},
			shouldPass:  false, // Should get mutated, not exempted
			description: "Pod with wrong owner name should not be exempted",
		},
		{
			name: "Case sensitive matching - different case should not match",
			pod: corev1.Pod{
				Metadata: &metav1.ObjectMeta{
					Name:      "cilium-agent-xyz",
					Namespace: "kube-system",
					OwnerReferences: []*metav1.OwnerReference{
						{
							Kind: func() *string { s := "DaemonSet"; return &s }(),
							Name: func() *string { s := "Cilium"; return &s }(), // Capital C
						},
					},
				},
				Spec: &corev1.PodSpec{},
			},
			settings: Settings{
				WorkloadTolerationKey: "workload",
				WorkloadNamespaceTag:  "Workload",
				AllowedApps: []AllowedApp{
					{Kind: "DaemonSet", Name: "cilium", Namespace: "kube-system"}, // lowercase c
				},
			},
			shouldPass:  false, // Should get mutated due to case mismatch
			description: "Name matching should be case sensitive",
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
			responsePayload, err := mutate(payload)
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

func TestPodMutationWithTolerationAddition(t *testing.T) {
	// Default settings for all tests
	settings := Settings{
		WorkloadTolerationKey: "workload",
		WorkloadNamespaceTag:  "Workload",
		AllowedApps:           []AllowedApp{},
	}

	testCases := []struct {
		name                string
		podName             string
		existingTolerations []*corev1.Toleration
		workloadValue       string
	}{
		{
			name:                "Pod gets toleration from namespace annotation",
			podName:             "test-app",
			existingTolerations: nil,
			workloadValue:       "frontend",
		},
		{
			name:    "Pod with existing tolerations gets additional workload toleration",
			podName: "database-app",
			existingTolerations: []*corev1.Toleration{
				{Key: "node-type", Operator: "Equal", Value: "gpu", Effect: "NoSchedule"},
			},
			workloadValue: "database",
		},
		{
			name:    "Pod with existing workload toleration gets it replaced",
			podName: "api-server",
			existingTolerations: []*corev1.Toleration{
				{Key: "workload", Operator: "Equal", Value: "old-value", Effect: "NoExecute"},
				{Key: "other", Operator: "Equal", Value: "keep-this", Effect: "NoSchedule"},
			},
			workloadValue: "api",
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			// Create pod with test data
			pod := corev1.Pod{
				Metadata: &metav1.ObjectMeta{
					Name:      tc.podName,
					Namespace: "test-namespace",
				},
				Spec: &corev1.PodSpec{
					Tolerations: tc.existingTolerations,
				},
			}

			// Create namespace with workload annotation
			namespace := corev1.Namespace{
				Metadata: &metav1.ObjectMeta{
					Name: "test-namespace",
					Annotations: map[string]string{
						"Workload": tc.workloadValue,
					},
				},
			}

			// Setup mock
			mockClient := &mocks.MockWapcClient{}

			namespaceRaw, err := json.Marshal(namespace)
			if err != nil {
				t.Fatalf("Failed to marshal namespace: %v", err)
			}

			// Use mock.Anything to accept any request bytes since marshaling might differ
			mockClient.On("HostCall", "kubewarden", "kubernetes", "get_resource", mock.Anything).Return(namespaceRaw, nil)
			host.Client = mockClient
			defer func() { host.Client = nil }()

			// Execute mutation
			payload, _ := kubewarden_testing.BuildValidationRequest(&pod, &settings)
			responsePayload, err := mutate(payload)
			if err != nil {
				t.Fatalf("Mutation failed: %v", err)
			}

			// Parse response
			var response kubewarden_protocol.ValidationResponse
			json.Unmarshal(responsePayload, &response)

			if !response.Accepted {
				t.Fatalf("Pod rejected: %v", response.Message)
			}
			if response.MutatedObject == nil {
				t.Fatal("Expected mutation but got none")
			}

			// Parse mutated pod - MutatedObject is base64 encoded JSON string
			var mutatedPod corev1.Pod
			mutatedBase64 := response.MutatedObject.(string)
			mutatedBytes, err := base64.StdEncoding.DecodeString(mutatedBase64)
			if err != nil {
				t.Fatalf("Cannot decode base64 mutated object: %v", err)
			}
			if err := json.Unmarshal(mutatedBytes, &mutatedPod); err != nil {
				t.Fatalf("Cannot unmarshal mutated pod: %v", err)
			}

			// Verify workload toleration exists with correct value
			found := false
			if mutatedPod.Spec == nil {
				t.Fatal("Mutated pod has nil Spec")
			}
			for _, tol := range mutatedPod.Spec.Tolerations {
				if tol != nil &&
					tol.Key == "workload" &&
					tol.Operator == "Equal" &&
					tol.Value == tc.workloadValue &&
					tol.Effect == "NoExecute" {
					found = true
					break
				}
			}
			if !found {
				t.Errorf("Expected workload toleration with value '%s' not found", tc.workloadValue)
			}
		})
	}
}
