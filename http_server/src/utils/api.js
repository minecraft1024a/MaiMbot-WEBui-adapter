/**
 * API工具类
 */

// 获取API基础地址
const getApiBase = () => {
  return new Promise(async (resolve) => {
    try {
      const response = await fetch('/server_config.json')
      const config = await response.json()
      const baseUrl = config.host && config.port 
        ? `http://${config.host}:${config.port}` 
        : 'http://127.0.0.1:8050'
      resolve(baseUrl)
    } catch (error) {
      console.warn('Failed to load server config, using default:', error)
      resolve('http://127.0.0.1:8050')
    }
  })
}

// 创建API请求函数
const createApiRequest = (endpoint, options = {}) => {
  return async (data = null) => {
    try {
      const apiBase = await getApiBase()
      const url = `${apiBase}${endpoint}`
      
      const defaultOptions = {
        headers: {
          'Content-Type': 'application/json',
        }
      }
      
      const finalOptions = {
        ...defaultOptions,
        ...options
      }
      
      if (data && (options.method === 'POST' || options.method === 'PUT')) {
        finalOptions.body = JSON.stringify(data)
      }
      
      const response = await fetch(url, finalOptions)
      const result = await response.json()
      
      if (!response.ok) {
        throw new Error(result.message || `HTTP error! status: ${response.status}`)
      }
      
      return result
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error)
      throw error
    }
  }
}

// 主题API
export const themeAPI = {
  get: createApiRequest('/theme', { method: 'GET' }),
  set: (theme) => createApiRequest('/theme', { method: 'POST' })({ theme })
}

// API密钥API
export const apiKeyAPI = {
  getAll: createApiRequest('/api_keys', { method: 'GET' }),
  set: (key, value) => createApiRequest('/api_key', { method: 'POST' })({ key, value })
}

// 数据库API
export const databaseAPI = {
  clearData: createApiRequest('/database/clear', { method: 'POST' }),
  clearDatabase: createApiRequest('/database', { method: 'DELETE' })
}

// 配置API
export const configAPI = {
  getBackground: createApiRequest('/background', { method: 'GET' }),
  setBackground: (url) => createApiRequest('/background', { method: 'POST' })({ url }),
  getSprite: createApiRequest('/sprite', { method: 'GET' }),
  setSprite: (url) => createApiRequest('/sprite', { method: 'POST' })({ url }),
  getAvatarConfig: createApiRequest('/avatar_config', { method: 'GET' }),
  setAvatarConfig: (config) => createApiRequest('/avatar_config', { method: 'POST' })(config)
}

export default {
  themeAPI,
  apiKeyAPI,
  databaseAPI,
  configAPI
}
