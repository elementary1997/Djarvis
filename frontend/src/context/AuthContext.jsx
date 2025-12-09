import React, { createContext, useContext, useState, useEffect } from 'react'
import Cookies from 'js-cookie'
import { authAPI } from '../services/api'

const AuthContext = createContext()

export const useAuth = () => {
  const context = useContext(AuthContext)
  if (!context) {
    throw new Error('useAuth must be used within AuthProvider')
  }
  return context
}

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    checkAuth()
  }, [])

  const checkAuth = async () => {
    const token = Cookies.get('access_token')
    if (token) {
      try {
        const response = await authAPI.getProfile()
        setUser(response.data)
      } catch (error) {
        console.error('Auth check failed:', error)
        Cookies.remove('access_token')
        Cookies.remove('refresh_token')
      }
    }
    setLoading(false)
  }

  const login = async (email, password) => {
    const response = await authAPI.login({ email, password })
    const { user, tokens } = response.data
    
    Cookies.set('access_token', tokens.access, { expires: 1 })
    Cookies.set('refresh_token', tokens.refresh, { expires: 7 })
    
    setUser(user)
    return user
  }

  const register = async (userData) => {
    const response = await authAPI.register(userData)
    const { user, tokens } = response.data
    
    Cookies.set('access_token', tokens.access, { expires: 1 })
    Cookies.set('refresh_token', tokens.refresh, { expires: 7 })
    
    setUser(user)
    return user
  }

  const logout = async () => {
    try {
      const refreshToken = Cookies.get('refresh_token')
      await authAPI.logout(refreshToken)
    } catch (error) {
      console.error('Logout error:', error)
    } finally {
      Cookies.remove('access_token')
      Cookies.remove('refresh_token')
      setUser(null)
    }
  }

  const updateUser = (userData) => {
    setUser({ ...user, ...userData })
  }

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    updateUser,
    isAuthenticated: !!user,
  }

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
