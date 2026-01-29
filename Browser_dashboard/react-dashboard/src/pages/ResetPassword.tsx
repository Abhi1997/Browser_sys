import React, { useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import { KeyRound, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { resetPassword } from '@/lib/api';

export default function ResetPassword() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get('token') ?? '';
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [done, setDone] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!token) {
      setError('Invalid reset link. Please request a new password reset.');
      return;
    }
    if (newPassword.length < 6) {
      setError('Password must be at least 6 characters.');
      return;
    }
    if (newPassword !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }
    setLoading(true);
    const result = await resetPassword(token, newPassword);
    setLoading(false);
    if (result.success) {
      setDone(true);
    } else {
      setError(result.error || 'Something went wrong. The link may have expired.');
    }
  };

  if (!token && !done) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-6">
        <div className="max-w-md w-full text-center rounded-xl border border-border bg-card p-6 shadow-lg">
          <KeyRound className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
          <h1 className="text-xl font-bold text-card-foreground mb-2">Invalid reset link</h1>
          <p className="text-muted-foreground mb-6">
            This link is missing the reset token. Please use the link from your email or request a new one.
          </p>
          <Button asChild variant="outline" className="gap-2">
            <Link to="/forgot-password">
              <ArrowLeft className="h-4 w-4" />
              Request new link
            </Link>
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-6">
      <div className="max-w-md w-full animate-slide-up rounded-xl border border-border bg-card p-6 shadow-lg">
        <div className="h-24 w-24 mx-auto rounded-2xl bg-primary/10 flex items-center justify-center mb-8">
          <KeyRound className="h-12 w-12 text-primary" />
        </div>
        <h1 className="text-2xl font-bold text-card-foreground text-center mb-2">
          Set new password
        </h1>
        <p className="text-muted-foreground text-center mb-8">
          Enter your new password below. It must be at least 6 characters.
        </p>

        {done ? (
          <div className="rounded-lg border border-border bg-card/50 p-6 text-center space-y-4">
            <p className="text-card-foreground">
              Your password has been reset. You can now log in with your new password from the browser application.
            </p>
            <Button asChild variant="outline" className="gap-2">
              <Link to="/">
                <ArrowLeft className="h-4 w-4" />
                Back to login
              </Link>
            </Button>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4 rounded-lg border border-border bg-card/50 p-6">
            <div>
              <label htmlFor="newPassword" className="text-sm font-medium text-card-foreground block mb-2">
                New password
              </label>
              <Input
                id="newPassword"
                type="password"
                placeholder="At least 6 characters"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                disabled={loading}
                minLength={6}
                autoFocus
                className="w-full"
              />
            </div>
            <div>
              <label htmlFor="confirmPassword" className="text-sm font-medium text-card-foreground block mb-2">
                Confirm password
              </label>
              <Input
                id="confirmPassword"
                type="password"
                placeholder="Confirm new password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                disabled={loading}
                minLength={6}
                className="w-full"
              />
            </div>
            {error && (
              <p className="text-sm text-destructive">{error}</p>
            )}
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? 'Resetting...' : 'Reset password'}
            </Button>
            <Button asChild variant="ghost" className="w-full gap-2">
              <Link to="/forgot-password">
                <ArrowLeft className="h-4 w-4" />
                Request new link
              </Link>
            </Button>
          </form>
        )}
      </div>
    </div>
  );
}
