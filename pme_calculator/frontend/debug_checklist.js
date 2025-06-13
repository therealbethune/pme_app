// 🔍 PME Calculator Debug Checklist
// Run this in the browser console after reproducing the error

console.log('🔍 PME Calculator Debug Checklist');
console.log('=' * 50);

// Step 1: Confirm upload state
console.log('\n1️⃣ Checking upload state...');
try {
    const uploads = window.app?.uploads;
    console.log('📊 window.app?.uploads:', uploads);
    
    if (uploads && typeof uploads === 'object' && Object.keys(uploads).length > 0) {
        console.log('✅ Upload state exists');
        Object.entries(uploads).forEach(([id, data]) => {
            console.log(`   📁 ${id}: ${data.name} (${data.status})`);
        });
    } else {
        console.log('❌ Upload state missing or empty');
        console.log('🔧 Fix: Ensure setUploads([...]) runs after await r.json()');
    }
} catch (e) {
    console.log('❌ Error checking upload state:', e.message);
}

// Step 2: Check fund ID in query
console.log('\n2️⃣ Checking fund ID in URL...');
try {
    const fundId = new URLSearchParams(location.search).get('fund_id');
    console.log('🔗 URL fund_id:', fundId);
    
    if (fundId) {
        console.log('✅ Fund ID found in URL');
    } else {
        console.log('❌ No fund ID in URL');
        console.log('🔧 Fix: After upload: location.href = `/analyze?fund_id=${id}`');
    }
} catch (e) {
    console.log('❌ Error checking URL:', e.message);
}

// Step 3: Validate API base
console.log('\n3️⃣ Checking API base URL...');
try {
    const apiBase = window.API_BASE;
    console.log('🌐 window.API_BASE:', apiBase);
    
    if (apiBase && apiBase.includes('localhost:8000')) {
        console.log('✅ API base looks correct');
    } else {
        console.log('❌ API base missing or incorrect');
        console.log('🔧 Fix: Set window.API_BASE = "http://localhost:8000"');
    }
} catch (e) {
    console.log('❌ Error checking API base:', e.message);
}

// Step 4: Check app instance and fund file ID
console.log('\n4️⃣ Checking app instance...');
try {
    const app = window.app;
    console.log('🎯 window.app:', app);
    
    if (app) {
        console.log('📊 app.fundFileId:', app.fundFileId);
        console.log('📈 app.benchmarkFileId:', app.benchmarkFileId);
        
        if (app.fundFileId) {
            console.log('✅ Fund file ID available');
        } else {
            console.log('❌ No fund file ID in app instance');
        }
    } else {
        console.log('❌ No app instance found');
        console.log('🔧 Fix: Ensure PMECalculatorPro is instantiated and assigned to window.app');
    }
} catch (e) {
    console.log('❌ Error checking app instance:', e.message);
}

// Step 5: Test raw fetch to health endpoint
console.log('\n5️⃣ Testing raw fetch...');
try {
    const apiBase = window.API_BASE || 'http://localhost:8000';
    console.log('🔗 Testing:', `${apiBase}/api/health`);
    
    fetch(`${apiBase}/api/health`)
        .then(r => {
            console.log('📡 Health check status:', r.status);
            if (r.status === 200) {
                console.log('✅ Server is reachable');
                return r.json();
            } else {
                console.log('❌ Server returned error status');
            }
        })
        .then(data => {
            if (data) {
                console.log('📄 Health response:', data);
            }
        })
        .catch(e => {
            console.log('❌ Fetch error:', e.message);
            if (e.message.includes('Failed to fetch')) {
                console.log('🔧 Possible CORS issue or server down');
            }
        });
} catch (e) {
    console.log('❌ Error testing fetch:', e.message);
}

// Step 6: Check for JavaScript errors
console.log('\n6️⃣ Checking for JavaScript errors...');
try {
    // Check if runAnalysis method exists
    const app = window.app;
    if (app && typeof app.runAnalysis === 'function') {
        console.log('✅ runAnalysis method exists');
    } else {
        console.log('❌ runAnalysis method missing');
    }
    
    // Check for common undefined variables
    const checks = [
        'fetch',
        'URLSearchParams',
        'console',
        'window'
    ];
    
    checks.forEach(check => {
        if (typeof window[check] !== 'undefined') {
            console.log(`✅ ${check} is available`);
        } else {
            console.log(`❌ ${check} is undefined`);
        }
    });
    
} catch (e) {
    console.log('❌ Error in JS checks:', e.message);
}

console.log('\n🎯 Debug checklist complete!');
console.log('📋 Next steps:');
console.log('1. Fix any ❌ issues found above');
console.log('2. Try the analysis again');
console.log('3. Check Network tab for the actual API call'); 