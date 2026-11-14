import type { CapacitorConfig } from '@capacitor/cli';

const config: CapacitorConfig = {
  appId: 'com.jusnie.costing',
  appName: 'Costing Planner',
  // Next.js writes a static export to `out/`; Capacitor packages that folder.
  webDir: 'out',
  server: {
    // Live reload on device: set CAP_SERVER_URL=http://<your-lan-ip>:3000 when developing.
    ...(process.env.CAP_SERVER_URL ? { url: process.env.CAP_SERVER_URL, cleartext: true } : {}),
    androidScheme: 'https',
  },
  ios: {
    contentInset: 'always',
  },
};

export default config;
