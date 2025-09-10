package main

import (
	"encoding/base64"
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
		verifyFunc          func(*testing.T, *corev1.Pod)
	}{
		{
			name:                "Pod gets toleration from namespace annotation",
			podName:             "test-app",
			existingTolerations: nil,
			workloadValue:       "frontend",
			verifyFunc: func(t *testing.T, pod *corev1.Pod) {
				if len(pod.Spec.Tolerations) != 1 {
					t.Errorf("Expected 1 toleration, got %d", len(pod.Spec.Tolerations))
				}
			},
		},
		{
			name:    "Pod with existing tolerations gets additional workload toleration",
			podName: "database-app",
			existingTolerations: []*corev1.Toleration{
				{Key: "node-type", Operator: "Equal", Value: "gpu", Effect: "NoSchedule"},
			},
			workloadValue: "database",
			verifyFunc: func(t *testing.T, pod *corev1.Pod) {
				if len(pod.Spec.Tolerations) != 2 {
					t.Errorf("Expected 2 tolerations, got %d", len(pod.Spec.Tolerations))
				}
				// Verify GPU toleration preserved
				found := false
				for _, tol := range pod.Spec.Tolerations {
					if tol != nil && tol.Key == "node-type" && tol.Value == "gpu" {
						found = true
						break
					}
				}
				if !found {
					t.Error("Original GPU toleration was not preserved")
				}
			},
		},
		{
			name:    "Pod with existing workload toleration gets it replaced",
			podName: "api-server",
			existingTolerations: []*corev1.Toleration{
				{Key: "workload", Operator: "Equal", Value: "old-value", Effect: "NoExecute"},
				{Key: "other", Operator: "Equal", Value: "keep-this", Effect: "NoSchedule"},
			},
			workloadValue: "api",
			verifyFunc: func(t *testing.T, pod *corev1.Pod) {
				// Verify old workload toleration is gone
				for _, tol := range pod.Spec.Tolerations {
					if tol != nil && tol.Key == "workload" && tol.Value == "old-value" {
						t.Error("Old workload toleration should have been replaced")
					}
				}
				// Verify other toleration preserved
				found := false
				for _, tol := range pod.Spec.Tolerations {
					if tol != nil && tol.Key == "other" && tol.Value == "keep-this" {
						found = true
						break
					}
				}
				if !found {
					t.Error("Non-workload toleration was not preserved")
				}
			},
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
			resourceRequest, _ := json.Marshal(&kubernetes.GetResourceRequest{
				APIVersion: "v1",
				Kind:       "Namespace",
				Name:       "default",
			})
			namespaceRaw, _ := json.Marshal(namespace)
			mockClient.On("HostCall", "kubewarden", "kubernetes", "get_resource", resourceRequest).Return(namespaceRaw, nil)
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

			// Run test-specific verification
			if tc.verifyFunc != nil {
				tc.verifyFunc(t, &mutatedPod)
			}
		})
	}
}

//go test -v
=== RUN   TestAllowedAppsAreNotMutated
=== RUN   TestAllowedAppsAreNotMutated/Cilium_DaemonSet_pod_should_not_be_mutated
--- PASS: TestAllowedAppsAreNotMutated (0.00s)
    --- PASS: TestAllowedAppsAreNotMutated/Cilium_DaemonSet_pod_should_not_be_mutated (0.00s)
=== RUN   TestPodMutationWithTolerationAddition
=== RUN   TestPodMutationWithTolerationAddition/Pod_gets_toleration_from_namespace_annotation
--- FAIL: TestPodMutationWithTolerationAddition (0.00s)
    --- FAIL: TestPodMutationWithTolerationAddition/Pod_gets_toleration_from_namespace_annotation (0.00s)
panic: 
        
        mock: Unexpected Method Call
        -----------------------------
        
        HostCall(string,string,string,[]uint8)
                        0: "kubewarden"
                        1: "kubernetes"
                        2: "get_resource"
                        3: []byte(nil)
        
        The closest call I have is: 
        
        HostCall(string,string,string,[]uint8)
                        0: "kubewarden"
                        1: "kubernetes"
                        2: "get_resource"
                        3: []byte{0x7b, 0x22, 0x61, 0x70, 0x69, 0x5f, 0x76, 0x65, 0x72, 0x73, 0x69, 0x6f, 0x6e, 0x22, 0x3a, 0x22, 0x76, 0x31, 0x22, 0x2c, 0x22, 0x6b, 0x69, 0x6e, 0x64, 0x22, 0x3a, 0x22, 0x4e, 0x61, 0x6d, 0x65, 0x73, 0x70, 0x61, 0x63, 0x65, 0x22, 0x2c, 0x22, 0x6e, 0x61, 0x6d, 0x65, 0x22, 0x3a, 0x22, 0x64, 0x65, 0x66, 0x61, 0x75, 0x6c, 0x74, 0x22, 0x2c, 0x22, 0x64, 0x69, 0x73, 0x61, 0x62, 0x6c, 0x65, 0x5f, 0x63, 0x61, 0x63, 0x68, 0x65, 0x22, 0x3a, 0x66, 0x61, 0x6c, 0x73, 0x65, 0x7d}
        
        Difference found in argument 3:
        
        --- Expected
        +++ Actual
        @@ -1,8 +1,2 @@
        -([]uint8) (len=78) {
        - 00000000  7b 22 61 70 69 5f 76 65  72 73 69 6f 6e 22 3a 22  |{"api_version":"|
        - 00000010  76 31 22 2c 22 6b 69 6e  64 22 3a 22 4e 61 6d 65  |v1","kind":"Name|
        - 00000020  73 70 61 63 65 22 2c 22  6e 61 6d 65 22 3a 22 64  |space","name":"d|
        - 00000030  65 66 61 75 6c 74 22 2c  22 64 69 73 61 62 6c 65  |efault","disable|
        - 00000040  5f 63 61 63 68 65 22 3a  66 61 6c 73 65 7d        |_cache":false}|
        -}
        +([]uint8) <nil>
         
        
        Diff: 0: PASS:  (string=kubewarden) == (string=kubewarden)
                1: PASS:  (string=kubernetes) == (string=kubernetes)
                2: PASS:  (string=get_resource) == (string=get_resource)
                3: FAIL:  ([]uint8=[]) != ([]uint8=[123 34 97 112 105 95 118 101 114 115 105 111 110 34 58 34 118 49 34 44 34 107 105 110 100 34 58 34 78 97 109 101 115 112 97 99 101 34 44 34 110 97 109 101 34 58 34 100 101 102 97 117 108 116 34 44 34 100 105 115 97 98 108 101 95 99 97 99 104 101 34 58 102 97 108 115 101 125])
        at: [/Users/Ingrid.A.Kovacs/Workspace/add-workload-toleration/vendor/github.com/kubewarden/policy-sdk-go/pkg/capabilities/mocks/mock_WapcClient.go:24 /Users/Ingrid.A.Kovacs/Workspace/add-workload-toleration/validate.go:149 /Users/Ingrid.A.Kovacs/Workspace/add-workload-toleration/validate.go:51 /Users/Ingrid.A.Kovacs/Workspace/add-workload-toleration/validate_test.go:220]
         [recovered, repanicked]

goroutine 10 [running]:
testing.tRunner.func1.2({0x1048f4d40, 0x140001cae40})
        /Users/Ingrid.A.Kovacs/Workspace/go/pkg/mod/golang.org/toolchain@v0.0.1-go1.25.0.darwin-arm64/src/testing/testing.go:1872 +0x190
testing.tRunner.func1()
