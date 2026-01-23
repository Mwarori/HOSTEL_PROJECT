/**
 * API Helper for Hostel Management System
 */

const API_BASE = '/api';
let currentUser = null;
let authToken = null;

// Initialize auth from localStorage
function initAuth() {
    const token = localStorage.getItem('access_token');
    const user = localStorage.getItem('user');
    if (token && user) {
        authToken = token;
        currentUser = JSON.parse(user);
        updateUIAfterLogin();
    }
}

async function apiCall(endpoint, method = 'GET', data = null) {
    const options = {
        method,
        headers: {
            'Content-Type': 'application/json',
        }
    };

    if (authToken) {
        options.headers['Authorization'] = `Bearer ${authToken}`;
    }

    if (data) {
        options.body = JSON.stringify(data);
    }

    try {
        const response = await fetch(`${API_BASE}${endpoint}`, options);
        const result = await response.json();
        
        if (response.status === 401) {
            logoutUser();
            window.location.href = '/login.html';
            return null;
        }
        
        if (!response.ok) {
            console.error('API Error:', result);
            return null;
        }
        
        return result;
    } catch (error) {
        console.error('Fetch Error:', error);
        alert('Connection error: ' + error.message);
        return null;
    }
}

// AUTH ENDPOINTS
async function register(email, password, name, role) {
    const result = await apiCall('/auth/register/', 'POST', {
        email, password, name, role
    });
    if (result && result.access) {
        authToken = result.access;
        currentUser = result.user;
        localStorage.setItem('access_token', authToken);
        localStorage.setItem('user', JSON.stringify(currentUser));
        return true;
    }
    return false;
}

async function login(email, password) {
    const result = await apiCall('/auth/login/', 'POST', {
        email, password
    });
    if (result && result.access) {
        authToken = result.access;
        currentUser = result.user;
        localStorage.setItem('access_token', authToken);
        localStorage.setItem('user', JSON.stringify(currentUser));
        return true;
    }
    return false;
}

function logoutUser() {
    authToken = null;
    currentUser = null;
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
}

function updateUIAfterLogin() {
    const logoutBtn = document.getElementById('logoutBtn');
    if (logoutBtn && currentUser) {
        logoutBtn.textContent = `Logout (${currentUser.email})`;
    }
}

// HOSTEL ENDPOINTS
async function getAllHostels() {
    return await apiCall('/hostels/');
}

async function getHostelDetail(hostelId) {
    return await apiCall(`/hostels/${hostelId}/`);
}

async function addHostel(data) {
    return await apiCall('/hostels/add/', 'POST', data);
}

async function updateHostel(hostelId, data) {
    return await apiCall(`/hostels/${hostelId}/update/`, 'PUT', data);
}

async function getMyHostels() {
    return await apiCall('/hostels/my/');
}

// ROOM ENDPOINTS
async function getHostelRooms(hostelId) {
    return await apiCall(`/rooms/hostel/${hostelId}/`);
}

async function addRoom(data) {
    return await apiCall('/rooms/add/', 'POST', data);
}

async function updateRoom(roomId, data) {
    return await apiCall(`/rooms/${roomId}/update/`, 'PUT', data);
}

// BOOKING ENDPOINTS
async function bookHostel(data) {
    return await apiCall('/bookings/book/', 'POST', data);
}

async function getMyBookings() {
    return await apiCall('/bookings/my/');
}

async function getOwnerBookings(hostelId) {
    return await apiCall(`/bookings/owner/${hostelId}/`);
}

async function approveBooking(bookingId, data) {
    return await apiCall(`/bookings/${bookingId}/approve/`, 'POST', data);
}

async function rejectBooking(bookingId, data) {
    return await apiCall(`/bookings/${bookingId}/reject/`, 'POST', data);
}

// ISSUE ENDPOINTS
async function reportIssue(data) {
    return await apiCall('/issues/report/', 'POST', data);
}

async function getOwnerIssues(hostelId) {
    return await apiCall(`/issues/owner/${hostelId}/`);
}

async function resolveIssue(issueId, data) {
    return await apiCall(`/issues/${issueId}/resolve/`, 'POST', data);
}

// NOTICE ENDPOINTS
async function sendNotice(data) {
    return await apiCall('/notices/send/', 'POST', data);
}

async function getNotices(hostelId) {
    return await apiCall(`/notices/${hostelId}/`);
}

// PAYMENT ENDPOINTS
async function getMyPayments() {
    return await apiCall('/payments/my/');
}

async function makePayment(data) {
    return await apiCall('/payments/make/', 'POST', data);
}

async function recordPayment(data) {
    return await apiCall('/payments/record/', 'POST', data);
}

async function getHostelPayments(hostelId) {
    return await apiCall(`/payments/hostel/${hostelId}/`);
}

// DASHBOARD ENDPOINTS
async function getStudentDashboard() {
    return await apiCall('/dashboard/student/');
}

async function getOwnerDashboard() {
    return await apiCall('/dashboard/owner/');
}

async function getHostelStats(hostelId) {
    return await apiCall(`/analytics/hostel/${hostelId}/`);
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', initAuth);
