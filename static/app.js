// API Base URL
const API_BASE = '';

// Current section
let currentSection = 'dashboard';

// Initialize the app
document.addEventListener('DOMContentLoaded', function() {
    showDashboard();
    setupEventListeners();
});

function setupEventListeners() {
    // Job form submission
    document.getElementById('job-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        await createJob();
    });

    // Resume form submission
    document.getElementById('resume-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        await uploadResume();
    });

    // Evaluate form submission
    document.getElementById('evaluate-form').addEventListener('submit', async function(e) {
        e.preventDefault();
        await evaluateResume();
    });
}

// Navigation functions
function showDashboard() {
    hideAllSections();
    document.getElementById('dashboard-section').classList.remove('hidden');
    currentSection = 'dashboard';
    loadDashboardData();
}

function showJobs() {
    hideAllSections();
    document.getElementById('jobs-section').classList.remove('hidden');
    currentSection = 'jobs';
    loadJobs();
}

function showResumes() {
    hideAllSections();
    document.getElementById('resumes-section').classList.remove('hidden');
    currentSection = 'resumes';
    loadResumes();
}

function showEvaluate() {
    hideAllSections();
    document.getElementById('evaluate-section').classList.remove('hidden');
    currentSection = 'evaluate';
    loadEvaluateOptions();
}

function hideAllSections() {
    document.querySelectorAll('.section').forEach(section => {
        section.classList.add('hidden');
    });
}

// Dashboard functions
async function loadDashboardData() {
    try {
        const [jobs, resumes, evaluations] = await Promise.all([
            fetch('/api/jobs?limit=100').then(r => r.json()),
            fetch('/api/resumes?limit=100').then(r => r.json()),
            fetch('/api/evaluations?limit=100').then(r => r.json())
        ]);

        // Update metrics
        document.getElementById('total-jobs').textContent = jobs.length;
        document.getElementById('total-resumes').textContent = resumes.length;
        document.getElementById('total-evaluations').textContent = evaluations.length;
        
        if (evaluations.length > 0) {
            const avgScore = evaluations.reduce((sum, eval) => sum + eval.final_score, 0) / evaluations.length;
            document.getElementById('avg-score').textContent = avgScore.toFixed(1) + '%';
        }

        // Update recent evaluations table
        updateEvaluationsTable(evaluations.slice(0, 10));

    } catch (error) {
        console.error('Error loading dashboard data:', error);
        showError('Failed to load dashboard data');
    }
}

function updateEvaluationsTable(evaluations) {
    const tbody = document.getElementById('evaluations-table-body');
    tbody.innerHTML = '';

    evaluations.forEach(eval => {
        const row = document.createElement('tr');
        row.className = 'border-b';
        
        const verdictClass = eval.verdict === 'High' ? 'text-green-600' : 
                           eval.verdict === 'Medium' ? 'text-yellow-600' : 'text-red-600';
        
        row.innerHTML = `
            <td class="px-4 py-2">${eval.candidate_name || 'N/A'}</td>
            <td class="px-4 py-2">${eval.job_title || 'N/A'}</td>
            <td class="px-4 py-2 font-semibold">${eval.final_score}%</td>
            <td class="px-4 py-2 ${verdictClass} font-semibold">${eval.verdict}</td>
            <td class="px-4 py-2">${new Date(eval.eval_time).toLocaleDateString()}</td>
        `;
        tbody.appendChild(row);
    });
}

// Jobs functions
async function loadJobs() {
    try {
        const response = await fetch('/api/jobs?limit=50');
        const jobs = await response.json();
        displayJobs(jobs);
    } catch (error) {
        console.error('Error loading jobs:', error);
        showError('Failed to load jobs');
    }
}

function displayJobs(jobs) {
    const container = document.getElementById('jobs-list');
    container.innerHTML = '';

    jobs.forEach(job => {
        const jobCard = document.createElement('div');
        jobCard.className = 'border border-gray-200 rounded-lg p-4';
        jobCard.innerHTML = `
            <div class="flex justify-between items-start">
                <div class="flex-1">
                    <h4 class="text-lg font-semibold text-gray-800">${job.title}</h4>
                    <p class="text-sm text-gray-600">ID: ${job.id}</p>
                    <p class="text-sm text-gray-600">Location: ${job.location || 'Not specified'}</p>
                    <p class="text-sm text-gray-600">Must-have: ${(job.must_have || []).join(', ')}</p>
                </div>
                <button onclick="bulkEvaluate(${job.id})" 
                        class="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600">
                    Bulk Evaluate
                </button>
            </div>
        `;
        container.appendChild(jobCard);
    });
}

async function createJob() {
    const formData = new FormData();
    formData.append('title', document.getElementById('job-title').value);
    formData.append('jd_text', document.getElementById('job-description').value);
    formData.append('must_have', document.getElementById('must-have').value);
    formData.append('nice_to_have', document.getElementById('nice-to-have').value);

    try {
        const response = await fetch('/api/jobs', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        
        if (response.ok) {
            showSuccess(`Job created successfully! ID: ${result.job_id}`);
            document.getElementById('job-form').reset();
            loadJobs();
        } else {
            showError('Failed to create job: ' + result.detail);
        }
    } catch (error) {
        console.error('Error creating job:', error);
        showError('Failed to create job');
    }
}

// Resumes functions
async function loadResumes() {
    try {
        const response = await fetch('/api/resumes?limit=50');
        const resumes = await response.json();
        displayResumes(resumes);
    } catch (error) {
        console.error('Error loading resumes:', error);
        showError('Failed to load resumes');
    }
}

function displayResumes(resumes) {
    const container = document.getElementById('resumes-list');
    container.innerHTML = '';

    resumes.forEach(resume => {
        const resumeCard = document.createElement('div');
        resumeCard.className = 'border border-gray-200 rounded-lg p-4';
        resumeCard.innerHTML = `
            <div class="flex justify-between items-start">
                <div class="flex-1">
                    <h4 class="text-lg font-semibold text-gray-800">${resume.candidate_name}</h4>
                    <p class="text-sm text-gray-600">Email: ${resume.candidate_email}</p>
                    <p class="text-sm text-gray-600">ID: ${resume.id}</p>
                    <p class="text-sm text-gray-600">Uploaded: ${new Date(resume.upload_time).toLocaleDateString()}</p>
                </div>
            </div>
        `;
        container.appendChild(resumeCard);
    });
}

async function uploadResume() {
    const formData = new FormData();
    formData.append('name', document.getElementById('candidate-name').value);
    formData.append('email', document.getElementById('candidate-email').value);
    formData.append('file', document.getElementById('resume-file').files[0]);

    try {
        const response = await fetch('/api/resumes', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        
        if (response.ok) {
            showSuccess(`Resume uploaded successfully! ID: ${result.resume_id}`);
            document.getElementById('resume-form').reset();
            loadResumes();
        } else {
            showError('Failed to upload resume: ' + result.detail);
        }
    } catch (error) {
        console.error('Error uploading resume:', error);
        showError('Failed to upload resume');
    }
}

// Evaluation functions
async function loadEvaluateOptions() {
    try {
        const [jobs, resumes] = await Promise.all([
            fetch('/api/jobs?limit=100').then(r => r.json()),
            fetch('/api/resumes?limit=100').then(r => r.json())
        ]);

        // Populate job select
        const jobSelect = document.getElementById('eval-job');
        jobSelect.innerHTML = '<option value="">Select a job...</option>';
        jobs.forEach(job => {
            const option = document.createElement('option');
            option.value = job.id;
            option.textContent = `${job.title} (ID: ${job.id})`;
            jobSelect.appendChild(option);
        });

        // Populate resume select
        const resumeSelect = document.getElementById('eval-resume');
        resumeSelect.innerHTML = '<option value="">Select a resume...</option>';
        resumes.forEach(resume => {
            const option = document.createElement('option');
            option.value = resume.id;
            option.textContent = `${resume.candidate_name} (ID: ${resume.id})`;
            resumeSelect.appendChild(option);
        });

    } catch (error) {
        console.error('Error loading evaluation options:', error);
        showError('Failed to load options');
    }
}

async function evaluateResume() {
    const formData = new FormData();
    formData.append('job_id', document.getElementById('eval-job').value);
    formData.append('resume_id', document.getElementById('eval-resume').value);

    try {
        const response = await fetch('/api/evaluate', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        
        if (response.ok) {
            displayEvaluationResults(result);
        } else {
            showError('Failed to evaluate: ' + result.detail);
        }
    } catch (error) {
        console.error('Error evaluating:', error);
        showError('Failed to evaluate');
    }
}

function displayEvaluationResults(result) {
    const container = document.getElementById('evaluation-results');
    const content = document.getElementById('results-content');
    
    const verdictClass = result.verdict === 'High' ? 'text-green-600' : 
                       result.verdict === 'Medium' ? 'text-yellow-600' : 'text-red-600';
    
    content.innerHTML = `
        <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
            <div class="text-center">
                <div class="text-4xl font-bold text-blue-600">${result.final_score}%</div>
                <div class="text-gray-600">Overall Score</div>
            </div>
            <div class="text-center">
                <div class="text-2xl font-bold ${verdictClass}">${result.verdict}</div>
                <div class="text-gray-600">Verdict</div>
            </div>
            <div class="text-center">
                <div class="text-2xl font-bold text-purple-600">${result.matched_skills?.length || 0}</div>
                <div class="text-gray-600">Skills Matched</div>
            </div>
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
                <h4 class="text-lg font-semibold text-green-600 mb-2">✅ Matched Skills</h4>
                <div class="bg-green-50 p-4 rounded">
                    ${result.matched_skills?.length ? 
                        result.matched_skills.map(skill => `<span class="inline-block bg-green-200 text-green-800 px-2 py-1 rounded mr-2 mb-2">${skill}</span>`).join('') :
                        '<p class="text-gray-500">No matched skills found</p>'
                    }
                </div>
            </div>
            <div>
                <h4 class="text-lg font-semibold text-red-600 mb-2">❌ Missing Skills</h4>
                <div class="bg-red-50 p-4 rounded">
                    ${result.missing_skills?.length ? 
                        result.missing_skills.map(skill => `<span class="inline-block bg-red-200 text-red-800 px-2 py-1 rounded mr-2 mb-2">${skill}</span>`).join('') :
                        '<p class="text-gray-500">No missing skills</p>'
                    }
                </div>
            </div>
        </div>
        
        <div class="mt-6">
            <h4 class="text-lg font-semibold mb-2">💡 Feedback</h4>
            <div class="bg-blue-50 p-4 rounded">
                <p class="text-gray-700">${result.feedback || 'No feedback available'}</p>
            </div>
        </div>
    `;
    
    container.classList.remove('hidden');
}

async function bulkEvaluate(jobId) {
    try {
        const formData = new FormData();
        formData.append('job_id', jobId);
        
        const response = await fetch('/api/bulk-evaluate', {
            method: 'POST',
            body: formData
        });
        const result = await response.json();
        
        if (response.ok) {
            showSuccess(`Bulk evaluation completed! Processed ${result.processed_count} resumes`);
            if (currentSection === 'dashboard') {
                loadDashboardData();
            }
        } else {
            showError('Bulk evaluation failed: ' + result.detail);
        }
    } catch (error) {
        console.error('Error in bulk evaluation:', error);
        showError('Bulk evaluation failed');
    }
}

// Utility functions
function showSuccess(message) {
    showNotification(message, 'success');
}

function showError(message) {
    showNotification(message, 'error');
}

function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `fixed top-4 right-4 p-4 rounded shadow-lg z-50 ${
        type === 'success' ? 'bg-green-500 text-white' : 'bg-red-500 text-white'
    }`;
    notification.textContent = message;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        document.body.removeChild(notification);
    }, 5000);
}