let video = document.getElementById('video');
let canvas = document.getElementById('canvas');
let photoPreview = document.getElementById('photoPreview');
let regForm = document.getElementById('regForm');
let reviewContainer = document.getElementById('reviewContainer');
let confirmBtn = document.getElementById('confirmSubmitBtn');
let stream = null;

// Initialize camera
document.addEventListener('DOMContentLoaded', function () {
  initCamera();
});

function initCamera() {
  if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
    navigator.mediaDevices.getUserMedia({ video: true })
      .then(mediaStream => {
        stream = mediaStream;
        video.srcObject = stream;
        video.play();
      })
      .catch(err => {
        console.error("Camera error: ", err);
        alert('Camera access denied or unavailable: ' + err.message);
      });
  } else {
    alert('MediaDevices API not supported in your browser');
  }
}

function takePhoto() {
  // Validate form first
  if (!validateForm()) {
    return;
  }

  if (!video.srcObject) {
    alert('Camera not initialized yet');
    return;
  }

  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;
  let context = canvas.getContext('2d');
  context.drawImage(video, 0, 0, canvas.width, canvas.height);

  // Stop camera to save memory
  if (stream) {
    let tracks = stream.getTracks();
    tracks.forEach(track => track.stop());
    video.srcObject = null;
  }

  // Show photo preview
  let dataURL = canvas.toDataURL('image/jpeg');
  photoPreview.src = dataURL;

  // Fill in preview info
  document.getElementById('previewName').innerText = regForm.name.value;
  document.getElementById('previewRoll').innerText = regForm.roll.value;
  document.getElementById('previewBranch').innerText = regForm.branch.value;
  document.getElementById('previewSection').innerText = regForm.section.value;
  document.getElementById('previewEmail').innerText = regForm.email.value;

  // Show review container
  reviewContainer.style.display = 'flex';
}

function validateForm() {
  // Check all required fields
  const requiredFields = regForm.querySelectorAll("[required]");
  for (let field of requiredFields) {
    if (!field.value.trim()) {
      alert(`Please fill in the ${field.placeholder} field`);
      field.focus();
      return false;
    }
  }
  
  // Validate email format
  const emailField = regForm.email;
  const emailPattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
  if (!emailPattern.test(emailField.value)) {
    alert('Please enter a valid email address');
    emailField.focus();
    return false;
  }
  
  return true;
}

function cancelReview() {
  // Hide review container
  reviewContainer.style.display = 'none';
  
  // Re-initialize camera
  initCamera();
}

// Form submit after preview
confirmBtn.addEventListener('click', () => {
  canvas.toBlob(function (blob) {
    let fileName = "photo_" + new Date().getTime() + ".jpg";
    let photoFile = new File([blob], fileName, { type: "image/jpeg" });

    const formData = new FormData(regForm);
    formData.append('photo', photoFile);

    fetch('/register', {
      method: 'POST',
      body: formData
    })
      .then(response => {
        if (response.ok) {
          alert('Form submitted successfully!');
          window.location.href = '/home';
        } else {
          response.text().then(text => {
            console.error("Server response:", text);
            alert(`Server error (${response.status}): ${text}`);
          });
        }
      })
      .catch(error => {
        console.error('Fetch error:', error);
        alert('Network error: ' + error.message);
      });
  }, 'image/jpeg', 0.95);
});