document.addEventListener('DOMContentLoaded', function() {
    const profileButton = document.getElementById('profile-button');
    const profileSidebar = document.getElementById('profile-sidebar');
    const closeSidebarButton = document.getElementById('close-sidebar');
    
    if (profileButton && profileSidebar) {
        profileButton.addEventListener('click', function() {
            profileSidebar.classList.add('active');
        });
        
        if (closeSidebarButton) {
            closeSidebarButton.addEventListener('click', function() {
                profileSidebar.classList.remove('active');
            });
        }
    }
    
    const forms = document.querySelectorAll('.needs-validation');
    
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            
            form.classList.add('was-validated');
        }, false);
    });
    
    const searchInput = document.getElementById('job-search');
    const jobCards = document.querySelectorAll('.job-card');
    
    if (searchInput && jobCards.length > 0) {
        searchInput.addEventListener('input', function() {
            const searchTerm = this.value.toLowerCase();
            
            jobCards.forEach(function(card) {
                const title = card.querySelector('.job-title').textContent.toLowerCase();
                const company = card.querySelector('.job-company').textContent.toLowerCase();
                const description = card.querySelector('.job-description').textContent.toLowerCase();
                
                if (title.includes(searchTerm) || company.includes(searchTerm) || description.includes(searchTerm)) {
                    card.style.display = '';
                } else {
                    card.style.display = 'none';
                }
            });
        });
    }
    
    const parseButton = document.getElementById('parse-resume-button');
    const progressBar = document.getElementById('parse-progress');
    const resultsContainer = document.getElementById('parse-results');
    
    if (parseButton && progressBar && resultsContainer) {
        parseButton.addEventListener('click', function() {
            progressBar.style.display = 'block';
            progressBar.style.width = '0%';
            
            let progress = 0;
            const interval = setInterval(function() {
                progress += 5;
                progressBar.style.width = progress + '%';
                progressBar.setAttribute('aria-valuenow', progress);
                
                if (progress >= 100) {
                    clearInterval(interval);
                    resultsContainer.style.display = 'block';
                }
            }, 100);
        });
    }
    
    const tabButtons = document.querySelectorAll('[data-tab-target]');
    const tabContents = document.querySelectorAll('[data-tab-content]');
    
    if (tabButtons.length > 0 && tabContents.length > 0) {
        tabButtons.forEach(button => {
            button.addEventListener('click', () => {
                const target = document.querySelector(button.dataset.tabTarget);
                
                tabContents.forEach(content => {
                    content.classList.remove('active');
                });
                
                tabButtons.forEach(btn => {
                    btn.classList.remove('active');
                });
                
                button.classList.add('active');
                target.classList.add('active');
            });
        });
    }
});