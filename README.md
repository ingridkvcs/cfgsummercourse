# cfgsummercourse
A Git Repository Example

This is my first change

This is my second change


package main

import (
	"encoding/json"
	"fmt"
	"testing"

	corev1 "github.com/kubewarden/k8s-objects/api/core/v1"
	storagev1 "github.com/kubewarden/k8s-objects/api/storage/v1"
	metav1 "github.com/kubewarden/k8s-objects/apimachinery/pkg/apis/meta/v1"
	kubernetes "github.com/kubewarden/policy-sdk-go/pkg/capabilities/kubernetes"
	mocks "github.com/kubewarden/policy-sdk-go/pkg/capabilities/mocks"
	kubewarden_protocol "github.com/kubewarden/policy-sdk-go/protocol"
)

// define test cases
var cases = []struct {
	name     string
	tenant   string
	userInfo kubewarden_protocol.UserInfo
	settings Settings
	valid    bool
	mutate   bool
}{
	{
		name:   "test valid from tenant group",
		tenant: "bps",
		userInfo: kubewarden_protocol.UserInfo{
			Groups: []string{
				"oidc-group:c5941e27-2065-4885-bba7-fdfdcad94ab4",
			},
		},
		settings: Settings{},
		valid:    true,
		mutate:   true,
	},
	{
		name:   "test valid from jenkins",
		tenant: "ccl",
		userInfo: kubewarden_protocol.UserInfo{
			Groups: []string{
				"oidc-group:ccl-jenkins",
			},
		},
		settings: Settings{},
		valid:    true,
		mutate:   true,
	},
	{
		name:   "test invalid storage class name",
		tenant: "ccl",
		userInfo: kubewarden_protocol.UserInfo{
			Groups: []string{
				"oidc-group:ccl-jenkins",
			},
		},
		settings: Settings{},
		valid:    false,
		mutate:   false,
	},
	{
		name:   "test allow system masters",
		tenant: "",
		userInfo: kubewarden_protocol.UserInfo{
			Groups: []string{
				"system:masters",
			},
		},
		settings: Settings{},
		valid:    true,
		mutate:   false,
	},
	{
		name:   "test allow service account",
		tenant: "",
		userInfo: kubewarden_protocol.UserInfo{
			Username: "system:serviceaccount:kube-system:cilium",
		},
		settings: Settings{
			AllowedServiceAccounts: []ServiceAccount{{
				Name:      "cilium",
				Namespace: "kube-system",
			}},
		},
		valid:  true,
		mutate: false,
	},
}

// tenant configmap data
var tenantConfigMap = corev1.ConfigMap{
	Data: map[string]string{
		"c5941e27-2065-4885-bba7-fdfdcad94ab4": "bps",
	},
}

func TestMutation(t *testing.T) {

	// setup mock host for tenant config map waPC call
	mock := &mocks.MockWapcClient{}
	namespace := "kube-system"
	resourceRequest, err := json.Marshal(&kubernetes.GetResourceRequest{
		APIVersion:   "v1",
		Kind:         "ConfigMap",
		Name:         "tenant-groups",
		Namespace:    &namespace,
		DisableCache: false,
	})
	if err != nil {
		t.Errorf("cannot marshall get resource request: %v", err)
	}

	tenantConfigMapRaw, err := json.Marshal(tenantConfigMap)
	if err != nil {
		t.Errorf("cannot marshall tenant configmap: %v", err)
	}

	mock.On("HostCall", "kubewarden", "kubernetes", "get_resource", resourceRequest).Return(tenantConfigMapRaw, nil)
	host.Client = mock

	// execute test cases
	for _, testCase := range cases {

		t.Logf("running: %s", testCase.name)

		// setup validation request

		storageClassName := "invalid-sc"
		if testCase.valid {
			storageClassName = fmt.Sprintf("%s-sc", testCase.tenant)
		}

		storageClassRaw, err := json.Marshal(storagev1.StorageClass{
			Metadata: &metav1.ObjectMeta{
				Name: storageClassName,
			},
		})
		if err != nil {
			t.Fatalf("cannot marshall storageclass: %v", err)
		}

		admissionRequest := kubewarden_protocol.KubernetesAdmissionRequest{
			Object:   storageClassRaw,
			UserInfo: testCase.userInfo,
		}

		settingsRaw, err := json.Marshal(testCase.settings)
		if err != nil {
			t.Fatalf("cannot marshall settings: %v", err)
			continue
		}

		request := kubewarden_protocol.ValidationRequest{
			Request:  admissionRequest,
			Settings: settingsRaw,
		}

		payload, err := json.Marshal(request)
		if err != nil {
			t.Fatalf("cannot marshall request: %+v", err)
		}

		// attempt to validate request
		responsePayload, err := validate(payload)
		if err != nil {
			t.Fatalf("error calling validate: %+v", err)
		}

		var response kubewarden_protocol.ValidationResponse
		if err = json.Unmarshal(responsePayload, &response); err != nil {
			t.Fatalf("cannot unmarshall response: %+v", err)
		}

		// check response matches expected
		if response.Accepted != testCase.valid {
			t.Fatalf("response '%v' does not match expected '%v'", response.Accepted, testCase.valid)
		}

		// parse mutated object

		if testCase.mutate && response.MutatedObject == nil {
			t.Fatalf("no mutated object in response")
		} else if !testCase.mutate && response.MutatedObject != nil {
			t.Fatalf("unexpected mutated object in response")
		}

		// not expecting mutate, skipping
		if !testCase.mutate {
			continue
		}

		mutatedRequestJSON, err := json.Marshal(response.MutatedObject.(map[string]interface{}))
		if err != nil {
			t.Fatalf("cannot marshal mutated object: %+v", err)
		}

		var mutatedStorageClass storagev1.StorageClass
		if err = json.Unmarshal(mutatedRequestJSON, &mutatedStorageClass); err != nil {
			t.Fatalf("cannot unmarshall object response: %+v", err)
		}

		// check labels match expected

		if mutatedStorageClass.Metadata.Labels == nil {
			t.Fatal("mutated storage class has no labels")
		}

		if val, ok := mutatedStorageClass.Metadata.Labels["tenant"]; ok {
			if val != testCase.tenant {
				t.Fatalf("mutated storage class tenant label '%v' does not match expected '%v'", val, testCase.tenant)
			}
		}
	}
}
