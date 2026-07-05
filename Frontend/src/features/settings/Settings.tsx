import { motion } from 'framer-motion';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Label } from '@/components/ui/label';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { Switch } from '@/components/ui/switch';

export default function Settings() {
  return (
    <div className="h-full w-full max-w-4xl mx-auto px-6 py-8 md:px-8 md:py-10 flex flex-col hide-scrollbar overflow-y-auto">
      <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="space-y-6 pb-12">
        
        <div>
          <h2 className="text-2xl font-semibold tracking-tight">Settings</h2>
          <p className="text-muted-foreground mt-1">Manage your account settings and preferences.</p>
        </div>

        <div className="grid gap-6">
          <Card className="border-border/40 bg-card/50 shadow-sm backdrop-blur-sm">
            <CardHeader>
              <CardTitle>Profile</CardTitle>
              <CardDescription>This is how others will see you on the site.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Display Name</Label>
                <Input id="name" defaultValue="Chronos User" className="max-w-md bg-background" />
              </div>
              <div className="space-y-2">
                <Label htmlFor="email">Email Address</Label>
                <Input id="email" defaultValue="user@example.com" disabled className="max-w-md bg-muted/50" />
              </div>
            </CardContent>
          </Card>

          <Card className="border-border/40 bg-card/50 shadow-sm backdrop-blur-sm">
            <CardHeader>
              <CardTitle>Appearance</CardTitle>
              <CardDescription>Customize the look and feel of the application.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between max-w-md">
                <div className="space-y-0.5">
                  <Label>Reduce Motion</Label>
                  <p className="text-sm text-muted-foreground">Minimize animations across the interface.</p>
                </div>
                <Switch />
              </div>
            </CardContent>
          </Card>

          <Card className="border-border/40 bg-card/50 shadow-sm backdrop-blur-sm">
            <CardHeader>
              <CardTitle>API Access</CardTitle>
              <CardDescription>Manage your API keys for programmatic access to Chronos.</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="apiKey">Active Key</Label>
                <div className="flex gap-2 max-w-md">
                  <Input id="apiKey" value="chr_************************" readOnly className="bg-muted/50 font-mono text-muted-foreground" />
                  <Button variant="outline">Regenerate</Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

      </motion.div>
    </div>
  );
}
