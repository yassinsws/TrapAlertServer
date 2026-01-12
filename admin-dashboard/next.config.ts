/** @type {import('next').NextConfig} */
const nextConfig = {
  async rewrites() {
    return [
      {
        source: '/api/:path*',
        destination: 'http://localhost:8000/api/:path*',
      },
      {
        source: '/feedback',
        destination: 'http://localhost:8000/feedback',
      },
    ];
  },
};

export default nextConfig;
