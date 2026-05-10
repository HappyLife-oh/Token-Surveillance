/**
 * Token Surveillance — DeepSeek API 本地代理
 * 监听 localhost:18999，转发到 api.deepseek.com
 * 从 /v1/chat/completions 响应中提取 usage 并记录
 */
const http = require('http')
const https = require('https')
const fs = require('fs')
const path = require('path')

const PORT = 18999
const UPSTREAM = 'api.deepseek.com'
const DATA_FILE = process.env.TS_DATA_FILE || path.join(
  process.env.APPDATA || '.', 'TokenSurveillance', 'usage_proxy.json'
)

function appendUsage(record) {
  try {
    const dir = path.dirname(DATA_FILE)
    if (!fs.existsSync(dir)) fs.mkdirSync(dir, { recursive: true })
    fs.appendFileSync(DATA_FILE, JSON.stringify(record) + '\n')
  } catch (_) {}
}

function proxyRequest(clientReq, clientRes) {
  const headers = { ...clientReq.headers }
  delete headers.host
  delete headers['content-length']

  const options = {
    hostname: UPSTREAM,
    port: 443,
    path: clientReq.url,
    method: clientReq.method,
    headers,
  }

  const proxyReq = https.request(options, (proxyRes) => {
    const chunks = []
    proxyRes.on('data', (c) => chunks.push(c))
    proxyRes.on('end', () => {
      const body = Buffer.concat(chunks)

      // Try to record usage from /v1/chat/completions responses
      if (clientReq.url.includes('/v1/chat/completions') && proxyRes.statusCode === 200) {
        try {
          const json = JSON.parse(body.toString())
          if (json.usage) {
            appendUsage({
              time: new Date().toISOString(),
              model: json.model || json.usage.model || '',
              prompt_tokens: json.usage.prompt_tokens || 0,
              completion_tokens: json.usage.completion_tokens || 0,
              total_tokens: json.usage.total_tokens || 0,
              prompt_cache_hit_tokens: json.usage.prompt_cache_hit_tokens || 0,
            })
          }
        } catch (_) {}
      }

      clientRes.writeHead(proxyRes.statusCode, proxyRes.headers)
      clientRes.end(body)
    })
  })

  proxyReq.on('error', (err) => {
    clientRes.writeHead(502)
    clientRes.end(JSON.stringify({ error: 'Proxy error', message: err.message }))
  })

  clientReq.on('data', (c) => proxyReq.write(c))
  clientReq.on('end', () => proxyReq.end())
}

const server = http.createServer(proxyRequest)
server.listen(PORT, () => {
  console.log(`[TS-Proxy] Listening on http://localhost:${PORT}`)
})

// Graceful shutdown
process.on('SIGTERM', () => server.close(() => process.exit(0)))
process.on('SIGINT', () => server.close(() => process.exit(0)))
