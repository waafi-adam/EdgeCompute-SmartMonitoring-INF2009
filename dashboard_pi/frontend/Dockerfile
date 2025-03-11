FROM node:22

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install

COPY . .

RUN npm install -g vite  # ✅ Ensure Vite is installed globally

EXPOSE 5173

CMD ["npm", "run", "dev"]
