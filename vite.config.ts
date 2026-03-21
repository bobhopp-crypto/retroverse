import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'
import fs from 'fs'

// https://vite.dev/config/
export default defineConfig({
  root: 'apps/web',
  plugins: [
    react(),
    {
      name: 'magazine-static',
      configureServer(server) {
        server.middlewares.use((req, res, next) => {
          const pUrl = req.url?.split('?')[0]
          if (pUrl === '/magazine' || pUrl === '/magazine/') {
            const p = path.join(server.config.root, 'public', 'magazine', 'index.html')
            if (fs.existsSync(p)) {
              res.statusCode = 200
              res.setHeader('Content-Type', 'text/html')
              fs.createReadStream(p).pipe(res)
              return
            }
          }
          next()
        })
      },
    },
  ],
  server: {
    proxy: {
      '/media': {
        target: (process.env.R2_PUBLIC_BASE || 'https://media.retroverse.live').replace(/\/+$/, ''),
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/media/, ''),
      },
    },
  },
})
