// topworx-new/src/core/auth/useUserRole.ts
// Returns the current user's role from AuthContext.
// Uses useAuth() hook instead of directly importing AuthContext (which is not exported).

import { useAuth } from './AuthProvider';
import { UserRole } from '../../app/navigation/modules';

export const useUserRole = (): UserRole => {
  const { user } = useAuth();
  return (user?.role as UserRole) || 'guest';
};
