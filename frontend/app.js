const API_BASE = '/api/v1';
let isLoginMode = true;

// Utility to get authorization headers
function getAuthHeaders() {
    const token = localStorage.getItem('token');
    return {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
    };
}

// Check auth state on page load
window.addEventListener('DOMContentLoaded', async () => {
    const token = localStorage.getItem('token');
    if (token) {
        await fetchUserProfile();
    }
});

// Toggle between Login and Register modes
function toggleAuthMode() {
    isLoginMode = !isLoginMode;
    document.getElementById('auth-title').innerText = isLoginMode ? 'Login' : 'Register';
    document.getElementById('auth-submit-btn').innerText = isLoginMode ? 'Login' : 'Register';
    document.getElementById('auth-toggle-text').innerText = isLoginMode ? "Don't have an account?" : "Already have an account?";
    document.getElementById('auth-toggle-btn').innerText = isLoginMode ? 'Register' : 'Login';
    document.getElementById('auth-error').classList.add('hidden');
}

// Handle Login or Register submit
async function handleAuth(event) {
    event.preventDefault();
    const email = document.getElementById('auth-email').value;
    const password = document.getElementById('auth-password').value;
    const errorDiv = document.getElementById('auth-error');
    errorDiv.classList.add('hidden');

    try {
        if (isLoginMode) {
            // Login expects application/x-www-form-urlencoded
            const formData = new URLSearchParams();
            formData.append('username', email);
            formData.append('password', password);

            const res = await fetch(`${API_BASE}/auth/login`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: formData
            });

            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || 'Login failed');

            localStorage.setItem('token', data.access_token);
            await fetchUserProfile();
        } else {
            // Register expects JSON
            const res = await fetch(`${API_BASE}/auth/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email, password })
            });

            const data = await res.json();
            if (!res.ok) throw new Error(data.detail || 'Registration failed');

            alert('Account created successfully! Please log in.');
            toggleAuthMode();
        }
    } catch (err) {
        errorDiv.innerText = err.message;
        errorDiv.classList.remove('hidden');
    }
}

// Fetch authenticated user profile
async function fetchUserProfile() {
    try {
        const res = await fetch(`${API_BASE}/auth/me`, {
            headers: getAuthHeaders()
        });

        if (!res.ok) throw new Error('Session expired');

        const user = await res.json();
        document.getElementById('user-email').innerText = user.email;
        document.getElementById('logout-btn').classList.remove('hidden');
        document.getElementById('auth-section').classList.add('hidden');
        document.getElementById('dashboard-section').classList.remove('hidden');

        fetchItems();
    } catch (err) {
        logout();
    }

    
}


// Logout
function logout() {
    localStorage.removeItem('token');
    document.getElementById('user-email').innerText = 'Not logged in';
    document.getElementById('logout-btn').classList.add('hidden');
    document.getElementById('auth-section').classList.remove('hidden');
    document.getElementById('dashboard-section').classList.add('hidden');
}

// Fetch user's saved items
async function fetchItems() {
    const listEl = document.getElementById('items-list');
    listEl.innerHTML = '<p class="text-slate-400">Loading items...</p>';

    try {
        const res = await fetch(`${API_BASE}/items/`, {
            headers: getAuthHeaders()
        });
        const items = await res.json();

        if (items.length === 0) {
            listEl.innerHTML = '<p class="text-slate-500 col-span-2">No items saved yet.</p>';
            return;
        }

        listEl.innerHTML = items.map(item => `
    <div class="bg-slate-800 p-4 rounded border border-slate-700 flex flex-col justify-between">
        <div>
            <div class="flex justify-between items-start mb-2">
                <span class="text-xs uppercase font-bold tracking-wider px-2 py-0.5 rounded ${item.item_type === 'link' ? 'bg-indigo-900/60 text-indigo-300' : 'bg-slate-700 text-slate-300'}">
                    ${item.item_type}
                </span>
                <span class="text-xs text-slate-500">${new Date(item.created_at).toLocaleDateString()}</span>
            </div>
            ${item.title ? `<h3 class="font-bold text-slate-200 mb-1">${escapeHtml(item.title)}</h3>` : ''}
            
            ${item.item_type === 'link' 
                ? `<a href="${escapeHtml(item.content)}" target="_blank" class="text-sky-400 hover:underline [word-break:break-word]">${escapeHtml(item.content)}</a>`
                : `<p class="text-slate-300 whitespace-pre-wrap [word-break:break-word]">${escapeHtml(item.content)}</p>`
            }
        </div>
        <div class="mt-4 pt-2 border-t border-slate-700 flex justify-end">
            <button onclick="deleteItem(${item.id})" class="text-xs text-rose-400 hover:text-rose-300">Delete</button>
        </div>
    </div>
`).join('');

    } catch (err) {
        listEl.innerHTML = '<p class="text-rose-400">Failed to load items.</p>';
    }
}

// Create new item
async function createItem(event) {
    event.preventDefault();
    const item_type = document.getElementById('item-type').value;
    const title = document.getElementById('item-title').value;
    const content = document.getElementById('item-content').value;

    try {
        const res = await fetch(`${API_BASE}/items/`, {
            method: 'POST',
            headers: getAuthHeaders(),
            body: JSON.stringify({ item_type, title, content })
        });

        if (!res.ok) throw new Error('Failed to create item');

        document.getElementById('item-title').value = '';
        document.getElementById('item-content').value = '';
        fetchItems();
    } catch (err) {
        alert(err.message);
    }
}

// Delete item
async function deleteItem(id) {
    if (!confirm('Are you sure you want to delete this item?')) return;

    try {
        const res = await fetch(`${API_BASE}/items/${id}`, {
            method: 'DELETE',
            headers: getAuthHeaders()
        });

        if (!res.ok) throw new Error('Failed to delete item');
        fetchItems();
    } catch (err) {
        alert(err.message);
    }
}

function escapeHtml(text) {
    if (!text) return '';
    return text.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}