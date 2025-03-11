FROM node:22-bullseye

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install --omit=dev

COPY . .

EXPOSE 5173

CMD ["npm", "run", "dev"]
