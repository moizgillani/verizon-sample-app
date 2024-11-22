function openModal(modalId) {
  document.getElementById(modalId).style.display = "block";
}

function closeModal(modalId) {
  document.getElementById(modalId).style.display = "none";
}

function submitAccessToken() {
  const clientId = document.getElementById("client_id").value;
  const clientSecret = document.getElementById("client_secret").value;

  fetch("/generate-access-token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: `client_id=${clientId}&client_secret=${clientSecret}`,
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.status === "success") {
        window.location.href = "/session-token";
      } else {
        alert(data.message);
      }
    });
}

function submitSessionToken() {
  const username = document.getElementById("uws_username").value;
  const password = document.getElementById("uws_password").value;

  fetch("/generate-session-token", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: `uws_username=${username}&uws_password=${password}`,
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.status === "success") {
        window.location.href = "/actions";
      } else {
        alert(data.message);
      }
    });
}

// Submit Change Device Custom Fields form
function submitChangeDevice() {
  alert("Change Device Custom Fields form submitted.");
  closeModal('changeDeviceModal');
}

// Submit Activate Device form
function submitActivateDevice() {
  const params = new URLSearchParams();
  params.append("device_id", document.getElementById("activate_device_id").value);
  params.append("device_kind", document.getElementById("activate_device_kind").value);
  params.append("account_name", document.getElementById("activate_account_name").value);
  params.append("service_plan", document.getElementById("activate_service_plan").value);
  params.append("mdn_zip_code", document.getElementById("activate_MDN_zip").value);
  params.append("sku_number", document.getElementById("activate_SKU_number").value);


  fetch("/activate-device", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: params.toString()
  })
  .then((response) => response.json())
  .then((data) => {
    if (data.status === "success") {
      if (data.data) {
        const params = new URLSearchParams({
          action: data.data.action,
          items: data.data.items,
        }).toString();
        window.location.href = `/result?${params}`;
      }
    } else {
      alert(data.message);
    }
  });
}

// Submit List Service Plans form
function submitListServicePlans() {
  const account_name = document.getElementById("service_plan_account_name").value;
  
  fetch("/get-service-plans", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: `account_name=${account_name}`,
  })
  .then((response) => response.json())
  .then((data) => {
    if (data.status === "success") {
      if (data.data) {
        const params = new URLSearchParams({
          action: data.data.action,
          items: data.data.items,
        }).toString();
        window.location.href = `/result?${params}`;
      }
    } else {
      alert(data.message);
    }
  });
}

// Submit List Device Information form
function submitListDeviceInfo() {
  const params = new URLSearchParams();
  params.append("device_id", document.getElementById("deviceInfo_device_id").value);
  params.append("device_kind", document.getElementById("deviceInfo_device_kind").value); // Add deviceID
  fetch("/get-device-info", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: params.toString()
  })
  .then((response) => response.json())
  .then((data) => {
    if (data.status === "success") {
      if (data.data) {
        const params = new URLSearchParams({
          action: data.data.action,
          items: data.data.items,
        }).toString();
        window.location.href = `/result?${params}`;
      }
    } else {
      alert(data.message);
    }
  });
}
