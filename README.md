package main

import (
	"encoding/json"
	"testing"

	corev1 "github.com/kubewarden/k8s-objects/api/core/v1"
	metav1 "github.com/kubewarden/k8s-objects/apimachinery/pkg/apis/meta/v1"
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
			name: "Pod not in allowed list should be processed normally",
			pod: corev1.Pod{
				Metadata: &metav1.ObjectMeta{
					Name:      "regular-app",
					Namespace: "default",
					OwnerReferences: []*metav1.OwnerReference{
						{
							Kind: func() *string { s := "Deployment"; return &s }(),
							Name: func() *string { s := "my-app"; return &s }(),
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
			shouldPass:  false, // Will be rejected because namespace fetch fails in test
			description: "Non-allowed apps should go through normal mutation process",
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
			name: "Same DaemonSet name but wrong namespace should not be allowed",
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
			shouldPass:  false,
			description: "Same app name in wrong namespace should not be treated as allowed",
		},
	}

	for _, tc := range testCases {
		t.Run(tc.name, func(t *testing.T) {
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
