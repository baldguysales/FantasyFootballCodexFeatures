/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  images: {
    domains: [
      'images.unsplash.com',
      'source.unsplash.com',
      'picsum.photos',
      'via.placeholder.com',
      'ffcodex.com',
      'www.ffcodex.com',
    ],
    formats: ['image/avif', 'image/webp'],
  },
  experimental: {
    // Enable new Next.js features
    appDir: true,
    // Enable server actions (if needed)
    serverActions: true,
  },
  // Enable CSS modules
  modularizeImports: {
    'lucide-react': {
      transform: 'lucide-react/dist/esm/icons/{{ kebabCase member }}',
    },
  },
  // Add custom webpack configurations if needed
  webpack: (config, { isServer }) => {
    // Add custom webpack configurations here
    return config;
  },
  // Add environment variables that should be exposed to the browser
  env: {
    NEXT_PUBLIC_APP_URL: process.env.NEXT_PUBLIC_APP_URL || 'http://localhost:3000',
  },
  // Add redirects and rewrites if needed
  async redirects() {
    return [
      {
        source: '/old-path/:path*',
        destination: '/new-path/:path*',
        permanent: false,
      },
    ];
  },
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: '/api/:path*',
      },
    ];
  },
  // Add headers for security
  async headers() {
    return [
      {
        source: '/(.*)',
        headers: [
          {
            key: 'X-Content-Type-Options',
            value: 'nosniff',
          },
          {
            key: 'X-Frame-Options',
            value: 'DENY',
          },
          {
            key: 'X-XSS-Protection',
            value: '1; mode=block',
          },
        ],
      },
    ];
  },
};

module.exports = nextConfig;
