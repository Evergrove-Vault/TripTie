FROM node:20-alpine as builder

WORKDIR /app

# Копируем зависимости
COPY package*.json ./
COPY next.config.ts ./
COPY tsconfig.json ./

# Устанавливаем зависимости
RUN npm ci

# Копируем исходный код
COPY src ./src
COPY public ./public

# Собираем приложение
RUN npm run build

# Продакшн этап
FROM node:18-alpine as runner

WORKDIR /app

# Создаем пользователя
RUN addgroup --system --gid 1001 nodejs
RUN adduser --system --uid 1001 nextjs

# Копируем собранное приложение
COPY --from=builder /app/public ./public
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

USER nextjs

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME="0.0.0.0"

CMD ["node", "server.js"]