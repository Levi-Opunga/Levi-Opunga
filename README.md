<img src="./assets/hero.svg?v=3f590fd" width="100%" alt="Levi Opunga, painted matatu-style. The LED route board reads 254 and cycles through Android, iOS, macOS, Windows, Linux and Web. The slogan reads: all screens, one codebase." />

I build products that run on every screen you own: phones, laptops, the browser, and the servers behind them. I work from Kenya, so M-Pesa payments and KRA tax filing are a normal part of the job.

### What I'm building

| Project | What it does | Stack |
|---|---|---|
| **Tessera** | A desktop SSH client that keeps your hosts, keys and snippets in a git repo you own. Secrets are [age](https://age-encryption.org)-encrypted per person before they're committed, so no company holds your credentials. | TypeScript, Electron, React |
| **Linky** | Links your phones and computers. Share the clipboard and files, mirror notifications, control media, or ring a lost phone, over the local network or through a relay. | Kotlin Multiplatform, Compose, Ktor |
| **Convo-Hub** | A platform for running business conversations on WhatsApp, with its own web app and a self-hosted deploy stack. | Kotlin, TypeScript, Docker |
| **Multi-store commerce** | One Medusa backend running six storefronts, from fragrance to coffee to a restaurant menu, each with its own theme and checkout. Plus a desktop point of sale. | Astro, Medusa, TypeScript |
| **Rent and tax** | Rent, leases and M-Pesa collection for landlords, and a gateway that files invoices with KRA eTIMS, retrying the ones that fail. | Hono, Drizzle, PostgreSQL, Go |
| **On-device AI** | Small local models that turn what you say into actions in a mobile app, without sending your words to a server. | React Native, Expo |
| **Logistics** | Live vehicle tracking, rider apps and dispatch dashboards. | Go, Expo, React |

### The numbers

<p>
  <img src="./metrics.stats.svg" width="49%" alt="GitHub contributions over the last 12 months, written as a mobile-money confirmation text" />
  <img src="./metrics.languages.svg" width="49%" alt="Most used languages across my repositories" />
</p>

<img src="https://raw.githubusercontent.com/Levi-Opunga/Levi-Opunga/output/snake.svg" width="100%" alt="A snake eating my contribution graph" />

### What I reach for

- **Mobile:** React Native and Expo, Kotlin and Compose Multiplatform, Android in Java, a little Swift when iOS demands it.
- **Web:** Next.js, Astro, React with TanStack, Svelte, Angular, Tailwind.
- **Backend:** Hono and Drizzle, Ktor, Spring Boot, Go, Medusa.
- **Data:** PostgreSQL, SQLite, MongoDB, MySQL, Redis, Neo4j, Supabase.
- **Shipping:** Docker, Traefik, GitHub Actions, Vercel, fastlane.

Next I'm learning OCaml and Haskell, on the way to writing my own compiler.

### Learned the hard way

- A new iOS app extension gets its own App ID. Associate the App Group with it, or signing fails.
- React Native has no `Buffer`. Your Node tests will pass anyway.
- App Store processing can reject a build without a word in the dashboard. Check your email.
- Never make a ScrollView the root of an expo-router tab.

<a href="https://twitter.com/badAtVim"><img src="./assets/footer.svg?v=3f590fd" width="100%" alt="Follow me on X: @badAtVim" /></a>
