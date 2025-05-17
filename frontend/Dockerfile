FROM node:20-alpine

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci --silent

COPY . .

RUN chown -R node:node /app/node_modules && \
    chmod -R 755 /app/node_modules

USER node

RUN npm run build

CMD ["npm", "start"]