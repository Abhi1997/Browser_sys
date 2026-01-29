import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import { Mail, ArrowLeft } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { forgotPassword } from '@/lib/api';

export default function ForgotPassword() {
  const [email, setEmail] = useState('');
  const [sent, setSent] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!email.trim()) {
      setError('Please enter your email address.');
      return;
    }
    setLoading(true);
    const result = await forgotPassword(email.trim());
    setLoading(false);
    if (result.success) {
      setSent(true);
    } else {
      setError(result.error || 'Something went wrong. Please try again.');
    }
  };

  return (
    <div className="min-h-screen bg-background flex items-center justify-center p-6">
      <div className="max-w-md w-full animate-slide-up rounded-xl border border-border bg-card p-6 shadow-lg">
        <div className="h-24 w-24 mx-auto rounded-2xl bg-primary/10 flex items-center justify-center mb-8">
          <Mail className="h-12 w-12 text-primary" />
        </div>
        <h1 className="text-2xl font-bold text-card-foreground text-center mb-2">
          Forgot password
        </h1>
        <p className="text-muted-foreground text-center mb-8">
          Enter the email address registered with your account. We'll send you a link to reset your password.
        </p>

        {sent ? (
          <div className="rounded-lg border border-border bg-card/50 p-6 text-center space-y-4">
            <p className="text-card-foreground">
              If an account exists with this email, you will receive a password reset link shortly.
              Check your inbox and spam folder.
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
              <label htmlFor="email" className="text-sm font-medium text-card-foreground block mb-2">
                Email address
              </label>
              <Input
                id="email"
                type="email"
                placeholder="you@example.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                disabled={loading}
                autoFocus
                className="w-full"
              />
            </div>
            {error && (
              <p className="text-sm text-destructive">{error}</p>
            )}
            <Button type="submit" className="w-full" disabled={loading}>
              {loading ? 'Sending...' : 'Send reset link'}
            </Button>
            <Button asChild variant="ghost" className="w-full gap-2">
              <Link to="/">
                <ArrowLeft className="h-4 w-4" />
                Back to login
              </Link>
            </Button>
          </form>
        )}
      </div>
    </div>
  );
}
