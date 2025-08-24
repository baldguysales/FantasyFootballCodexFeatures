import type { NextAuthConfig, Session, User } from "next-auth"
import CredentialsProvider from "next-auth/providers/credentials"

export const authConfig: NextAuthConfig = {
  // Add your authentication configuration here
  pages: {
    signIn: "/auth/signin",
    signOut: "/auth/signout",
    error: "/auth/error",
  },
  providers: [
    // Add your authentication providers here
    CredentialsProvider({
      name: 'Credentials',
      credentials: {
        email: { label: "Email", type: "email" },
        password: { label: "Password", type: "password" }
      },
      async authorize() {
        // This is a stub - replace with your actual authentication logic
        return null
      }
    })
  ],
  callbacks: {
    async session({ session, token }): Promise<Session> {
      if (token?.id) {
        // @ts-ignore - Adding custom property to session
        session.user.id = token.id as string
      }
      return session
    },
    async jwt({ token, user }) {
      if (user) {
        token.id = user.id
      }
      return token
    },
  },
  session: { strategy: "jwt" },
  secret: process.env.AUTH_SECRET || "your-secret-key",
}
