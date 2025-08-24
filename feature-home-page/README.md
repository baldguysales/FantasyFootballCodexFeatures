# Fantasy Football Codex - Marketing Site

A modern, responsive marketing website for Fantasy Football Codex built with Next.js 14, TypeScript, and Tailwind CSS.

## Features

- 🚀 Next.js 14 with App Router
- 🎨 Tailwind CSS for styling
- 🌓 Dark/light mode with system preference support
- 📱 Fully responsive design
- ⚡ Optimized for performance and SEO
- 🛠️ Developer-friendly with TypeScript

## Getting Started

### Prerequisites

- Node.js 18.0.0 or later
- npm or yarn

### Installation

1. Clone the repository
   ```bash
   git clone https://github.com/yourusername/fantasy-football-codex.git
   cd feature-home-page
   ```

2. Install dependencies
   ```bash
   npm install
   # or
   yarn
   # or
   pnpm install
   ```

3. Start the development server
   ```bash
   npm run dev
   # or
   yarn dev
   # or
   pnpm dev
   ```

4. Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.

## Available Scripts

- `dev` - Start the development server
- `build` - Build the application for production
- `start` - Start the production server
- `lint` - Run ESLint
- `lint:fix` - Fix ESLint issues
- `type-check` - Run TypeScript type checking

## Project Structure

```
src/
  app/                    # App Router
    (marketing)/          # Marketing pages
      layout.tsx          # Marketing layout
      page.tsx            # Home page
  components/            # Reusable components
    ui/                  # UI components (button, card, etc.)
  data/                  # Data files
    mocks/               # Mock data for development
  lib/                   # Utility functions
  styles/                # Global styles
```

## Environment Variables

Create a `.env.local` file in the root directory and add the following:

```env
NEXT_PUBLIC_APP_URL=http://localhost:3000
# Add other environment variables here
```

## Deployment

### Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-docs) from the creators of Next.js.

### Other Platforms

You can also deploy to other platforms like Netlify, AWS, or your own server. Refer to the [Next.js deployment documentation](https://nextjs.org/docs/deployment) for more details.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [Next.js Documentation](https://nextjs.org/docs)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [shadcn/ui](https://ui.shadcn.com/)
- [Lucide Icons](https://lucide.dev/)
