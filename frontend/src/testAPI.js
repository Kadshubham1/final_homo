import axios from 'axios'
import Cookies from 'js-cookie'

const API_BASE_URL = 'http://localhost:8000/api'

async function testEndpoints() {
  try {
    console.log('🧪 Testing API Endpoints\n')

    // 1. Login
    console.log('1️⃣  Testing Login...')
    const loginRes = await axios.post(`${API_BASE_URL}/auth/login/`, {
      username: 'admin@central.com',
      password: 'admin123'
    })
    const accessToken = loginRes.data.access
    console.log(`✅ Login successful`)
    console.log(`   Token: ${accessToken.substring(0, 50)}...`)

    const headers = { Authorization: `Bearer ${accessToken}` }

    // 2. Get Users
    console.log('\n2️⃣  Testing Get Users...')
    const usersRes = await axios.get(`${API_BASE_URL}/auth/users/`, { headers })
    console.log(`✅ Users loaded: ${usersRes.data.length} users`)
    usersRes.data.forEach(u => console.log(`   - ${u.username} (${u.role})`))

    // 3. Get Files
    console.log('\n3️⃣  Testing Get Files...')
    const filesRes = await axios.get(`${API_BASE_URL}/files/`, { headers })
    console.log(`✅ Files loaded: ${filesRes.data.results?.length || 0} files`)

    // 4. Get Sent Shares
    console.log('\n4️⃣  Testing Get Sent Shares...')
    const sharesRes = await axios.get(`${API_BASE_URL}/sharing/sent/`, { headers })
    console.log(`✅ Shares loaded: ${sharesRes.data.length} shares`)

    console.log('\n' + '='.repeat(50))
    console.log('✅ All endpoints working!')
    console.log('='.repeat(50))
  } catch (error) {
    console.error('❌ Error:', error.response?.data || error.message)
  }
}

testEndpoints()
