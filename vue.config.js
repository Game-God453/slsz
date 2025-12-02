const { defineConfig } = require('@vue/cli-service')
const webpack = require('webpack')

module.exports = defineConfig({
  publicPath: '/', 
  transpileDependencies: true,
  configureWebpack: {
    resolve: {
      fallback: {
        process: require.resolve('process/browser')
      }
    },
    plugins: [
      new webpack.ProvidePlugin({
        process: 'process/browser'
      })
    ]
  },
  // 添加开发服务器代理配置
  devServer: {
    proxy: {
      '/api': {
        target: 'http://116.62.208.67:8000',
        changeOrigin: true,
        pathRewrite: {
          '^/api': ''  // 去掉/api前缀
        }
      }
    }
  }
})
