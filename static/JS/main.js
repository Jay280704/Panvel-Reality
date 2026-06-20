// ===== PROPERTY STORAGE DATA =====
let props = [];

let activeTab = 'all';
let currentProp = null;

// ===== CORE ENGINE HANDLERS =====
function renderProps(list) {
  const g = document.getElementById('prop-grid');
  if (!g) return; // Agar dusre page par ho jahan grid nahi hai
  const nr = document.getElementById('no-res');
  if (!list.length) {
    g.innerHTML = '';
    if (nr) nr.style.display = 'block';
    return;
  }
  if (nr) nr.style.display = 'none';
  
  g.innerHTML = list.map(p => `
    <div class="prop-card">
      <div class="prop-img-wrap">
        <img src="${p.img}" alt="${p.name}" loading="lazy">
        <span class="pbadge ${p.purpose === 'rent' ? 'rent' : ''}">${p.badge}</span>
        <span class="ptype">${p.type.charAt(0).toUpperCase() + p.type.slice(1)}</span>
      </div>
      <div class="prop-body">
        <div class="prop-price">${p.price}</div>
        <div class="prop-name">${p.name}</div>
        <div class="prop-loc">
          <i class="fa-solid fa-location-dot" style="color: var(--gold); margin-right: 6px;"></i> ${p.loc}
        </div>
        <div class="prop-feats">
          ${p.area !== '—' ? `<div class="pfeat"><i class="fa-solid fa-expand" style="color: var(--purple-mid); margin-right: 4px;"></i> <strong>${p.area}</strong></div>` : ''}
          ${p.beds !== '—' ? `<div class="pfeat"><i class="fa-solid fa-bed" style="color: var(--purple-mid); margin-right: 4px;"></i> <strong>${p.beds}</strong></div>` : ''}
          ${p.bath !== '—' ? `<div class="pfeat"><i class="fa-solid fa-bath" style="color: var(--purple-mid); margin-right: 4px;"></i> <strong>${p.bath} Bath</strong></div>` : ''}
          ${p.parking !== '—' ? `<div class="pfeat"><i class="fa-solid fa-car" style="color: var(--purple-mid); margin-right: 4px;"></i> <strong>${p.parking}P</strong></div>` : ''}
        </div>
        <div class="prop-btns">
          <button class="pbtn-enquire" onclick="openModal(${p.id})">Enquire Now <i class="fa-solid fa-arrow-right" style="margin-left: 4px;"></i></button>
          <button class="pbtn-wa" onclick="waQuick(${p.id})" title="WhatsApp" aria-label="Enquire via WhatsApp">
            <i class="fa-brands fa-whatsapp"></i>
          </button>
          <button class="pbtn-call" onclick="callAgent()" title="Call Agent" aria-label="Call Agent">
            <i class="fa-solid fa-phone"></i>
          </button>
        </div>
      </div>
    </div>
  `).join('');
}

function setTab(el, f) {
  document.querySelectorAll('.ftab').forEach(t => t.classList.remove('active'));
  el.classList.add('active');
  activeTab = f;
  applyFilters();
}

function applyFilters() {
  let list = props;
  if (activeTab !== 'all') {
    list = list.filter(p => p.type === activeTab || p.purpose === activeTab);
  }
  renderProps(list);
}

function filterProps() {
  const type = document.getElementById('s-type')?.value;
  const purpose = document.getElementById('s-purpose')?.value;
  const budget = document.getElementById('s-budget')?.value;
  const kw = document.getElementById('s-kw')?.value?.toLowerCase() || '';
  
  let list = props;
  if (type) list = list.filter(p => p.type === type);
  if (purpose) list = list.filter(p => p.purpose === purpose);
  
  if (budget) {
    const bv = parseFloat(budget);
    if (bv === 999) {
      list = list.filter(p => p.purpose === 'buy' && p.priceV >= 100);
    } else {
      list = list.filter(p => {
        if (p.purpose === 'rent') return true; 
        return p.priceV <= bv;
      });
    }
  }
  
  if (kw) list = list.filter(p => p.name.toLowerCase().includes(kw) || p.loc.toLowerCase().includes(kw));
  
  const grid = document.getElementById('prop-grid');
  if (grid) {
    renderProps(list);
  } else {
    // Redirect to /properties page with search params
    const params = new URLSearchParams();
    if (type) params.set('type', type);
    if (purpose) params.set('purpose', purpose);
    if (budget) params.set('budget', budget);
    if (kw) params.set('kw', kw);
    window.location.href = '/properties?' + params.toString();
  }
}

// ===== MODAL CONTROLS =====
let currentSlideIndex = 0;
let carouselImages = [];

function openModal(id) {
  const p = props.find(x => x.id === id);
  if (!p) return;
  currentProp = p;
  
  carouselImages = p.images && p.images.length > 0 ? p.images : [p.img];
  currentSlideIndex = 0;
  
  // Build slides
  const wrapper = document.getElementById('carousel-wrapper');
  if (wrapper) {
    wrapper.innerHTML = carouselImages.map(img => `
      <div class="modal-slide">
        <img src="${img}" alt="${p.name}">
      </div>
    `).join('');
  }
  
  // Build dots
  const dotsContainer = document.getElementById('carousel-dots');
  if (dotsContainer) {
    dotsContainer.innerHTML = carouselImages.map((_, idx) => `
      <div class="carousel-dot ${idx === 0 ? 'active' : ''}" onclick="goToSlide(${idx})"></div>
    `).join('');
  }
  
  // Build thumbnails
  const thumbsContainer = document.getElementById('carousel-thumbs');
  if (thumbsContainer) {
    thumbsContainer.innerHTML = carouselImages.map((img, idx) => `
      <img class="carousel-thumb ${idx === 0 ? 'active' : ''}" src="${img}" alt="Thumb ${idx}" onclick="goToSlide(${idx})">
    `).join('');
  }
  
  // Hide controls if only 1 image
  const prevBtn = document.querySelector('.carousel-prev');
  const nextBtn = document.querySelector('.carousel-next');
  if (carouselImages.length <= 1) {
    if (prevBtn) prevBtn.style.display = 'none';
    if (nextBtn) nextBtn.style.display = 'none';
    if (dotsContainer) dotsContainer.style.display = 'none';
    if (thumbsContainer) thumbsContainer.style.display = 'none';
  } else {
    if (prevBtn) prevBtn.style.display = 'flex';
    if (nextBtn) nextBtn.style.display = 'flex';
    if (dotsContainer) dotsContainer.style.display = 'flex';
    if (thumbsContainer) thumbsContainer.style.display = 'flex';
  }
  
  updateCarousel();
  
  document.getElementById('m-title').textContent = p.name;
  document.getElementById('m-price').textContent = p.price;
  document.getElementById('m-msg').value = 'Interested in: ' + p.name + ' (' + p.loc + ')';
  document.getElementById('m-success').style.display = 'none';
  const feats = document.getElementById('m-feats');
  
  feats.innerHTML = [
    p.area !== '—' ? `<span style="background:var(--purple-light); color:var(--purple); padding:6px 14px; border-radius:20px; font-size:12px; font-weight:600;"><i class="fa-solid fa-expand" style="margin-right: 4px;"></i> ${p.area}</span>` : '',
    p.beds !== '—' ? `<span style="background:var(--purple-light); color:var(--purple); padding:6px 14px; border-radius:20px; font-size:12px; font-weight:600;"><i class="fa-solid fa-bed" style="margin-right: 4px;"></i> ${p.beds}</span>` : '',
    p.bath !== '—' ? `<span style="background:var(--purple-light); color:var(--purple); padding:6px 14px; border-radius:20px; font-size:12px; font-weight:600;"><i class="fa-solid fa-bath" style="margin-right: 4px;"></i> ${p.bath} Bath</span>` : '',
  ].join('');
  
  document.getElementById('modal').classList.add('open');
}

function updateCarousel() {
  const wrapper = document.getElementById('carousel-wrapper');
  if (wrapper) {
    wrapper.style.transform = `translateX(-${currentSlideIndex * 100}%)`;
  }
  
  document.querySelectorAll('.carousel-dot').forEach((dot, idx) => {
    if (idx === currentSlideIndex) {
      dot.classList.add('active');
    } else {
      dot.classList.remove('active');
    }
  });
  
  document.querySelectorAll('.carousel-thumb').forEach((thumb, idx) => {
    if (idx === currentSlideIndex) {
      thumb.classList.add('active');
      thumb.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' });
    } else {
      thumb.classList.remove('active');
    }
  });
}

function moveSlide(dir) {
  if (carouselImages.length === 0) return;
  currentSlideIndex = (currentSlideIndex + dir + carouselImages.length) % carouselImages.length;
  updateCarousel();
}

function goToSlide(idx) {
  currentSlideIndex = idx;
  updateCarousel();
}

function closeModal() {
  document.getElementById('modal').classList.remove('open');
}

function submitModal() {
  const name = document.getElementById('m-name').value.trim();
  const phone = document.getElementById('m-phone').value.trim();
  const message = document.getElementById('m-msg').value.trim();
  
  if (!name || !phone) {
    alert('Please fill your name and phone number!');
    return;
  }
  
  // Prepare data matching contact form fields
  const formData = new URLSearchParams();
  formData.append('name', name);
  formData.append('phone', phone);
  formData.append('email', '');
  
  if (currentProp) {
    formData.append('looking_for', currentProp.purpose === 'rent' ? 'Rent Property' : 'Buy Property');
    
    // Map backend expected property type options
    let pTypeDisplay = 'Flat / Apartment';
    if (currentProp.type === 'shop') pTypeDisplay = 'Shop / Commercial';
    else if (currentProp.type === 'plot') pTypeDisplay = 'Plot / Land';
    else if (currentProp.type === 'building') pTypeDisplay = 'Building';
    else if (currentProp.type === 'office') pTypeDisplay = 'Office Space';
    formData.append('prop_type', pTypeDisplay);
    
    formData.append('budget', currentProp.price);
  } else {
    formData.append('looking_for', 'Buy Property');
    formData.append('prop_type', 'Flat / Apartment');
    formData.append('budget', 'Any Budget');
  }
  
  formData.append('message', message);
  
  // Disable button or change text to loading
  const submitBtn = document.querySelector('.mbtn-sub');
  const originalText = submitBtn ? submitBtn.textContent : 'Send Enquiry';
  if (submitBtn) {
    submitBtn.disabled = true;
    submitBtn.innerHTML = 'Sending <i class="fa-solid fa-spinner fa-spin" style="margin-left: 6px;"></i>';
  }
  
  fetch('/submit-enquiry', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded'
    },
    body: formData.toString()
  })
  .then(response => {
    if (response.ok) {
      document.getElementById('m-success').style.display = 'block';
      // Clear inputs
      document.getElementById('m-name').value = '';
      document.getElementById('m-phone').value = '';
      setTimeout(() => {
        closeModal();
        document.getElementById('m-success').style.display = 'none';
      }, 2800);
    } else {
      alert('Something went wrong. Please try again.');
    }
  })
  .then(() => {
    // Sync counts in background if admin dashboard is open in another tab
  })
  .catch(err => {
    console.error('Error submitting enquiry:', err);
    alert('Error submitting enquiry. Please check your connection.');
  })
  .finally(() => {
    if (submitBtn) {
      submitBtn.disabled = false;
      submitBtn.textContent = originalText;
    }
  });
}

// ===== MESSAGING REDIRECTIONS =====
function waEnquire() {
  if (!currentProp) return;
  const name = document.getElementById('m-name').value || 'Customer';
  const msg = `Hello Panvel Realty! Mera naam ${name} hai. Mujhe is property me interest hai:%0A%0A*${currentProp.name}*%0ALocation: ${currentProp.loc}%0APrice: ${currentProp.price}%0A%0APlease contact me.`;
  window.open(`https://wa.me/919326552977?text=${msg}`, '_blank');
}

function waQuick(id) {
  const p = props.find(x => x.id === id);
  if (!p) return;
  const msg = `Hello Panvel Realty! Mujhe is property me interest hai:%0A*${p.name}*%0ALocation: ${p.loc}%0APrice: ${p.price}%0A%0APlease contact me.`;
  window.open(`https://wa.me/919326552977?text=${msg}`, '_blank');
}

function callAgent() {
  window.location.href = 'tel:+919326552977';
}

function submitContact() {
  const name = document.getElementById('c-name').value.trim();
  const phone = document.getElementById('c-phone').value.trim();
  if (!name || !phone) {
    alert('Please fill name and phone number!');
    return;
  }
  document.getElementById('contact-success').style.display = 'block';
  setTimeout(() => document.getElementById('contact-success').style.display = 'none', 5000);
}

function toggleNav() {
  const n = document.getElementById('mob-nav');
  if (n) n.classList.toggle('open');
}

// Initialize components if targets exist
document.addEventListener("DOMContentLoaded", () => {
  // Fetch properties from dynamic backend
  fetch('/api/properties')
    .then(res => res.json())
    .then(data => {
      props = data;

      // Check if URL has search parameters and pre-fill input values
      const params = new URLSearchParams(window.location.search);
      const type = params.get('type');
      const purpose = params.get('purpose');
      const budget = params.get('budget');
      const kw = params.get('kw');
      
      const typeEl = document.getElementById('s-type');
      const purposeEl = document.getElementById('s-purpose');
      const budgetEl = document.getElementById('s-budget');
      const kwEl = document.getElementById('s-kw');

      if (typeEl && type) typeEl.value = type;
      if (purposeEl && purpose) purposeEl.value = purpose;
      if (budgetEl && budget) budgetEl.value = budget;
      if (kwEl && kw) kwEl.value = kw;

      const grid = document.getElementById('prop-grid');
      if (grid) {
        filterProps();
      } else {
        renderProps(props);
      }
    })
    .catch(err => {
      console.error("Error loading properties:", err);
    });

  const mOverlay = document.getElementById('modal');
  if (mOverlay) {
    mOverlay.addEventListener('click', function(e) { 
      if (e.target === this) closeModal(); 
    });
  }
});