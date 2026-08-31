import NextAuth from 'next-auth';
import { authConfig } from './auth.config';

const authMiddleware = NextAuth(authConfig).auth;

export default authMiddleware;

export const config = {
  matcher: ['/((?!api|_next/static|_next/image|favicon.ico).*)'],
};
