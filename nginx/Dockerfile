FROM node:alpine AS builder

WORKDIR /app

COPY frontend/package*,json .

RUN npm ci

COPY frontend/ .

RUN npm run build

FROM nginx:alpine

COPY /nginx/default.conf /etc/nginx/conf.d/default.conf

COPY --from=builder app/build /usr/share/nginx/html

EXPOSE 80

