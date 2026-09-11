/** @type {import('next').NextConfig} */
const nextConfig = {
  output: 'export',
  trailingSlash: true,
  images: {
    unoptimized: true,
  },
  // Only use basePath and assetPrefix in production
  ...(process.env.NODE_ENV === 'production' ? {
    basePath: '',
    assetPrefix: '',
  } : {})
}

module.exports = nextConfig 