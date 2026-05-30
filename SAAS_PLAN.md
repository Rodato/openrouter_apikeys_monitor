# OpenRouter Monitor → SaaS Plan

## Visión del producto

**"Monitorea y controla los costos de tus APIs de IA — alertas automáticas, reportes diarios, límites por proyecto."**

### Value proposition
- 📊 Dashboard web con métricas en tiempo real
- 🔔 Alertas vía Telegram cuando superas umbrales
- 📈 Reportes diarios automáticos
- 👥 Multi-tenant: cada usuario conecta su OpenRouter Management Key
- 🎯 Límites por proyecto, alertas configurables
- 📱 Sin instalar nada — todo en la nube

---

## Arquitectura SaaS

### Stack propuesto

**Frontend:**
- Next.js 15 (App Router)
- shadcn/ui para componentes
- Recharts para gráficas
- TailwindCSS
- Deploy: Vercel

**Backend:**
- Next.js API Routes (serverless functions)
- PostgreSQL (Vercel Postgres o Supabase)
- Prisma ORM
- Cron jobs: Vercel Cron o Inngest

**Auth:**
- Clerk (integración nativa Vercel)

**Infra:**
- Vercel (frontend + API + DB + Cron)
- Todo en un solo proyecto

### Data Model (Prisma schema)

```prisma
model User {
  id                String    @id @default(cuid())
  email             String    @unique
  clerkId           String    @unique
  createdAt         DateTime  @default(now())
  
  // OpenRouter credentials
  openrouterManagementKey String?  @db.Text
  
  // Telegram config
  telegramBotToken    String?
  telegramChatId      String?
  
  // Settings
  dailyReportEnabled  Boolean   @default(true)
  dailyReportHour     Int       @default(9)
  timezone            String    @default("UTC")
  
  projects            Project[]
  alerts              Alert[]
}

model Project {
  id                String    @id @default(cuid())
  userId            String
  user              User      @relation(fields: [userId], references: [id])
  
  // OpenRouter key info
  keyName           String    // Nombre de la key en OpenRouter
  label             String    // Display name
  alertMonthlyUsd   Float     @default(10.0)
  
  enabled           Boolean   @default(true)
  createdAt         DateTime  @default(now())
  
  usageSnapshots    UsageSnapshot[]
  
  @@unique([userId, keyName])
}

model UsageSnapshot {
  id              String    @id @default(cuid())
  projectId       String
  project         Project   @relation(fields: [projectId], references: [id])
  
  timestamp       DateTime  @default(now())
  
  // Snapshot de métricas de OpenRouter
  usageDaily      Float
  usageWeekly     Float
  usageMonthly    Float
  usageTotal      Float
  limitRemaining  Float?
  disabled        Boolean   @default(false)
  
  @@index([projectId, timestamp])
}

model Alert {
  id              String    @id @default(cuid())
  userId          String
  user            User      @relation(fields: [userId], references: [id])
  
  projectKeyName  String
  timestamp       DateTime  @default(now())
  
  usageMonthly    Float
  threshold       Float
  percentage      Float
  
  sent            Boolean   @default(false)
  sentAt          DateTime?
}
```

---

## Features MVP (v1)

### 1. Landing page
- Explica qué hace el servicio
- Pricing simple (free tier + pro)
- "Sign up with GitHub" (Clerk)

### 2. Onboarding flow
```
1. Sign up → Clerk auth
2. Connect OpenRouter
   - Input: Management Key
   - Validación: fetch /keys para verificar que funciona
   - Guardado encriptado en DB
3. (Opcional) Connect Telegram
   - Crear bot con @BotFather
   - Input: Bot Token + Chat ID
   - Test: enviar mensaje de prueba
4. Agregar proyectos
   - Fetch automático de todas las keys del usuario
   - Checkboxes para seleccionar cuáles monitorear
   - Input: threshold por proyecto
5. Dashboard listo ✅
```

### 3. Dashboard principal

**Secciones:**

**Header:**
- Account credits (total / consumed / remaining)
- Last refresh timestamp
- "Refresh now" button

**Projects table:**
| Project | Today | Week | Month | Total | Limit | Status | Actions |
|---------|-------|------|-------|-------|-------|--------|---------|
| AMA Bot | $0.45 | $2.34 | $12.50 / $200 | $456 | $487.50 | ✅ 6% | 🔔 ⚙️ |

**Model breakdown (chart):**
- Pie chart: top 5 models by cost
- Bar chart: daily usage últimos 7 días

**Recent alerts:**
- Historial de alertas enviadas

### 4. Project detail page

**Ruta:** `/dashboard/projects/:id`

**Muestra:**
- Gráfica de uso diario (últimos 30 días)
- Tabla de activity breakdown por modelo
- Config: editar threshold, labels
- Historial de alertas de este proyecto

### 5. Settings page

**Secciones:**

**OpenRouter:**
- Management Key (oculto, editable)
- "Test connection" button
- "Sync projects" — refetch keys

**Telegram:**
- Bot Token
- Chat ID
- "Send test message" button
- Daily report enabled (toggle)
- Daily report hour (dropdown)

**Account:**
- Email
- Timezone
- Delete account

---

## Backend jobs (Cron)

### Job 1: Snapshot collector
**Frequency:** Every 5 minutes

```typescript
// app/api/cron/collect-snapshots/route.ts
export async function GET(req: Request) {
  const users = await db.user.findMany({
    where: { openrouterManagementKey: { not: null } },
    include: { projects: true }
  })
  
  for (const user of users) {
    const client = new OpenRouterClient(user.openrouterManagementKey)
    const keys = await client.getKeys()
    
    for (const project of user.projects) {
      const keyData = keys.find(k => k.name === project.keyName)
      if (!keyData) continue
      
      await db.usageSnapshot.create({
        data: {
          projectId: project.id,
          usageDaily: keyData.usage_daily,
          usageWeekly: keyData.usage_weekly,
          usageMonthly: keyData.usage_monthly,
          usageTotal: keyData.usage,
          limitRemaining: keyData.limit_remaining,
          disabled: keyData.disabled
        }
      })
      
      // Check threshold alerts
      if (keyData.usage_monthly >= project.alertMonthlyUsd) {
        await triggerAlert(user, project, keyData)
      }
    }
  }
  
  return Response.json({ ok: true })
}
```

### Job 2: Daily report sender
**Frequency:** Hourly (checks if it's 9 AM per user timezone)

```typescript
// app/api/cron/send-daily-reports/route.ts
export async function GET(req: Request) {
  const users = await db.user.findMany({
    where: { 
      dailyReportEnabled: true,
      telegramBotToken: { not: null }
    },
    include: { projects: true }
  })
  
  for (const user of users) {
    const userTime = DateTime.now().setZone(user.timezone)
    if (userTime.hour !== user.dailyReportHour) continue
    
    const report = await buildTelegramReport(user)
    await sendTelegramMessage(user.telegramBotToken, user.telegramChatId, report)
  }
  
  return Response.json({ ok: true })
}
```

---

## Pricing modelo

### Free tier
- ✅ Hasta 3 proyectos
- ✅ Alertas por Telegram
- ✅ Reportes diarios
- ✅ Dashboard web
- ✅ 30 días de historial

### Pro ($9/mes)
- ✅ Proyectos ilimitados
- ✅ 365 días de historial
- ✅ Email alerts (además de Telegram)
- ✅ Slack integration
- ✅ Exportar reportes CSV
- ✅ API webhook notifications

### Enterprise (custom)
- ✅ Todo lo de Pro
- ✅ Multi-user (equipos)
- ✅ SSO
- ✅ Soporte prioritario

---

## Roadmap features

**v1.1 — Alerts avanzados:**
- Email notifications
- Webhook notifications
- Slack integration
- Discord integration

**v1.2 — Analytics:**
- Cost breakdown por modelo
- Predicción de gasto mensual
- Anomaly detection (picos inusuales)

**v1.3 — Budget management:**
- Set hard limits (pausar key automáticamente)
- Presupuestos mensuales por proyecto
- Alerts escalonadas (80%, 90%, 100%)

**v1.4 — Multi-provider:**
- Soportar Anthropic API directamente
- OpenAI API
- Unified dashboard de todos los providers

**v1.5 — Teams:**
- Workspaces compartidos
- Role-based access
- Shared billing

---

## Tech Stack decisions

### ¿Por qué Next.js + Vercel?

**Pros:**
- Full-stack en un solo proyecto
- Vercel Postgres integrado
- Vercel Cron nativo
- Deploy automático desde GitHub
- Serverless → escala automático
- Edge functions para dashboard rápido
- Clerk auth nativo

**Cons:**
- Vendor lock-in (pero fácil migrar a Railway/Render si es necesario)

### ¿Por qué Clerk?

- Integración Vercel Marketplace (1-click)
- UI components pre-hechos
- Free tier generoso (10k MAU)
- SSO listo para Enterprise

### Database: Vercel Postgres vs Supabase

**Vercel Postgres (Neon):**
- ✅ Mismo dashboard que el proyecto
- ✅ Serverless (escala a 0)
- ✅ Simple setup
- ⚠️ Más caro a escala

**Supabase:**
- ✅ Free tier más generoso
- ✅ Real-time subscriptions (útil para dashboard live)
- ✅ Row-level security
- ⚠️ Otro servicio que gestionar

**Recomendación:** Empezar con Vercel Postgres, migrar a Supabase si crece.

---

## Monetization strategy

### Pricing psychology
- Free tier para hobbistas (3 proyectos suficiente para personal)
- $9/mes atractivo para freelancers/small teams
- Enterprise para agencies

### Revenue projections (conservative)

**Año 1:**
- 100 free users
- 20 pro users → $180/mes → $2,160/año
- 2 enterprise → $200/mes → $4,800/año
- **Total: ~$7k/año**

**Año 2:**
- 500 free users
- 100 pro users → $900/mes → $10,800/año
- 10 enterprise → $1,000/mes → $12,000/año
- **Total: ~$23k/año**

### Costos operativos

**Vercel:**
- Free tier hasta ~$20/mes de infra
- Pro plan: $20/mes cuando superes límites
- **Estimado:** $20-50/mes en año 1

**Profit margin:** ~80% (SaaS típico)

---

## Go-to-market

### Target audience
1. **AI agencies** — Gestionan múltiples proyectos con OpenRouter
2. **Indie hackers** — Build AI apps, quieren controlar costos
3. **Empresas** — Compliance, budgets, reporting

### Distribution channels
1. **Product Hunt** — Launch day
2. **Reddit** — r/OpenAI, r/LocalLLaMA, r/MachineLearning
3. **Twitter** — AI builder community
4. **OpenRouter Discord** — Organic users
5. **Content marketing** — "How to control your AI API costs"

### Partnerships
- Listarse en OpenRouter website (si tienen directory)
- Integrarse con otras herramientas (n8n, Zapier, Make)

---

## Development plan

### Phase 1: Core MVP (2-3 semanas)
- [ ] Setup Next.js + Vercel
- [ ] Prisma schema + migrations
- [ ] Clerk auth integration
- [ ] Onboarding flow (connect OpenRouter + Telegram)
- [ ] Dashboard principal (projects table)
- [ ] Settings page
- [ ] Cron job: snapshot collector
- [ ] Cron job: daily reports

### Phase 2: Polish (1 semana)
- [ ] Landing page
- [ ] Pricing page
- [ ] Project detail page con gráficas
- [ ] Stripe integration (subscriptions)
- [ ] Email confirmations

### Phase 3: Launch (1 semana)
- [ ] Testing con usuarios beta
- [ ] Product Hunt assets
- [ ] Docs + Help center
- [ ] Deploy production

**Timeline total: 4-5 semanas part-time**

---

## Next steps

¿Quieres que empecemos a construir el SaaS?

Puedo ayudarte con:

1. **Scaffold del proyecto Next.js** con toda la estructura
2. **Prisma schema** + migraciones iniciales
3. **Dashboard components** con shadcn/ui
4. **API routes** para OpenRouter integration
5. **Vercel deployment** configurado

¿Por dónde empezamos? 🚀
