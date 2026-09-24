FROM node:22-alpine

RUN npm install -g pnpm@8

WORKDIR /app

COPY package.json pnpm-lock.yaml ./
RUN pnpm install

EXPOSE 7888

CMD ["pnpm", "dev", "--host"]
