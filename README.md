package main

import (
	"encoding/json"
	"testing"

	corev1 "github.com/kubewarden/k8s-objects/api/core/v1"
	metav1 "github.com/kubewarden/k8s-objects/apimachinery/pkg/apis/meta/v1"
	kubernetes "github.com/kubewarden/policy-sdk-go/pkg/capabilities/kubernetes"
	mocks "github.com/kubewarden/policy-sdk-go/pkg/capabilities/mocks"
	kubewarden_protocol "github.com/kubewarden/policy-sdk-go/protocol"
	kubewarden_testing "github.com/kubewarden/policy-sdk-go/testing"
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
	// Test that pods get tolerations added based on namespace annotation
	
	testCases := []struct {
		name              string
		pod               corev1.Pod
		namespace         corev1.Namespace
		settings          Settings
		expectedToleration *corev1.Toleration
		description       string
	}{
		{
			name: "Pod gets toleration from namespace annotation",
			pod: corev1.Pod{
				Metadata: &metav1.ObjectMeta{
					Name:      "test-app",
					Namespace: "production",
				},
				Spec: &corev1.PodSpec{},
			},
			namespace: corev1.Namespace{
				Metadata: &metav1.ObjectMeta{
					Name: "production",
					Annotations: map[string]string{
						"Workload": "frontend",
					},
				},
			},
			settings: Settings{
				WorkloadTolerationKey: "workload",
				WorkloadNamespaceTag:  "Workload",
				AllowedApps:          []AllowedApp{},
			},
			expectedToleration: &corev1.Toleration{
				Key:      "workload",
				Operator: "Equal",
				Value:    "frontend",
				Effect:   "NoExecute",
			},
			description: "Pod should have workload toleration added from namespace annotation",
		},
		{
			name: "Pod with existing tolerations gets additional workload toleration",
			pod: corev1.Pod{
				Metadata: &metav1.ObjectMeta{
					Name:      "database-app",
					Namespace: "backend",
				},
				Spec: &corev1.PodSpec{
					Tolerations: []*corev1.Toleration{
						{
							Key:      "node-type",
							Operator: "Equal",
							Value:    "gpu",
							Effect:   "NoSchedule",
						},
					},
				},
			},
			namespace: corev1.Namespace{
				Metadata: &metav1.ObjectMeta{
					Name: "backend",
					Annotations: map[string]string{
						"Workload": "database",
					},
				},
			},
			settings: Settings{
				WorkloadTolerationKey: "workload",
				WorkloadNamespaceTag:  "Workload",
				AllowedApps:          []AllowedApp{},
			},
			expectedToleration: &corev1.Toleration{
				Key:      "workload",
				Operator: "Equal",
				Value:    "database",
				Effect:   "NoExecute",
			},
			description: "Pod should keep existing tolerations and add workload toleration",
		},
		{
			name: "Pod with existing workload toleration gets it replaced",
			pod: corev1.Pod{
				Metadata: &metav1.ObjectMeta{
					Name:      "api-server",
					Namespace: "services",
				},
				Spec: &corev1.PodSpec{
					Tolerations: []*corev1.Toleration{
						{
							Key:      "workload",
							Operator: "Equal",
							Value:    "old-value",
							Effect:   "NoExecute",
						},
						{
							Key:      "other",
							Operator: "Equal",
							Value:    "keep-this",
							Effect:   "NoSchedule",
						},
					},
				},
			},
			namespace: corev1.Namespace{
				Metadata: &metav1.ObjectMeta{
					Name: "services",
					Annotations: map[string]string{
						"Workload": "api",
					},
				},
			},
			settings: Settings{
				WorkloadTolerationKey: "workload",
				WorkloadNamespaceTag:  "Workload",
				AllowedApps:          []AllowedApp{},
			},
			expectedToleration: &corev1.Toleration{
				Key:      "workload",
				Operator: "Equal",
				Value:    "api",
				Effect:   "NoExecute",
			},
			description: "Existing workload toleration should be replaced with new value",
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
			// Setup mock for namespace fetch
			mockClient := &mocks.MockWapcClient{}
			
			// Build the expected namespace request
			resourceRequest, _ := json.Marshal(&kubernetes.GetResourceRequest{
				APIVersion: "v1",
				Kind:       "Namespace",
				Name:       "default", // BuildValidationRequest doesn't set namespace, so it defaults to "default"
			})
			
			// Marshal the namespace response
			namespaceRaw, _ := json.Marshal(tc.namespace)
			
			// Setup mock expectation
			mockClient.On("HostCall", "kubewarden", "kubernetes", "get_resource", resourceRequest).Return(namespaceRaw, nil)
			
			// Set the mock client
			host.Client = mockClient
			
			// Build validation request
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
			
			// Verify mutation was accepted
			if !response.Accepted {
				t.Errorf("%s: Expected pod to be accepted, but it was rejected. Message: %v",
					tc.description, response.Message)
			}
			
			// Verify mutation occurred
			if response.MutatedObject == nil {
				t.Fatalf("%s: Expected mutation but got none", tc.description)
			}
			
			// Parse mutated pod
			mutatedPodJSON, err := json.Marshal(response.MutatedObject)
			if err != nil {
				t.Fatalf("Cannot marshal mutated object: %v", err)
			}
			
			var mutatedPod corev1.Pod
			if err := json.Unmarshal(mutatedPodJSON, &mutatedPod); err != nil {
				t.Fatalf("Cannot unmarshal mutated pod: %v", err)
			}
			
			// Verify the expected toleration exists
			found := false
			for _, toleration := range mutatedPod.Spec.Tolerations {
				if toleration.Key == tc.expectedToleration.Key &&
					toleration.Operator == tc.expectedToleration.Operator &&
					toleration.Value == tc.expectedToleration.Value &&
					toleration.Effect == tc.expectedToleration.Effect {
					found = true
					break
				}
			}
			
			if !found {
				t.Errorf("%s: Expected toleration not found in mutated pod. Tolerations: %+v",
					tc.description, mutatedPod.Spec.Tolerations)
			}
			
			// For the test with existing tolerations, verify other tolerations are preserved
			if tc.name == "Pod with existing tolerations gets additional workload toleration" {
				if len(mutatedPod.Spec.Tolerations) != 2 {
					t.Errorf("Expected 2 tolerations, got %d", len(mutatedPod.Spec.Tolerations))
				}
				// Check that the GPU toleration is still there
				foundGPU := false
				for _, toleration := range mutatedPod.Spec.Tolerations {
					if toleration.Key == "node-type" && toleration.Value == "gpu" {
						foundGPU = true
						break
					}
				}
				if !foundGPU {
					t.Errorf("Original GPU toleration was not preserved")
				}
			}
			
			// For the replacement test, verify old workload toleration is gone
			if tc.name == "Pod with existing workload toleration gets it replaced" {
				for _, toleration := range mutatedPod.Spec.Tolerations {
					if toleration.Key == "workload" && toleration.Value == "old-value" {
						t.Errorf("Old workload toleration should have been replaced but still exists")
					}
				}
				// Verify other tolerations are preserved
				foundOther := false
				for _, toleration := range mutatedPod.Spec.Tolerations {
					if toleration.Key == "other" && toleration.Value == "keep-this" {
						foundOther = true
						break
					}
				}
				if !foundOther {
					t.Errorf("Non-workload toleration was not preserved")
				}
			}
			
			// Clean up mock for next test
			host.Client = nil
		})
	}
}
