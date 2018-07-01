/* eslint-disable no-template-curly-in-string */
import Router, { Resource } from 'tg-resources';

const getHeaders = () => ({
  Authorization: 'Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJleHAiOjE1MzA1NTAwNDUsInVzZXJuYW1lIjoidGVzdEB0ZXN0LmNvbSIsImVtYWlsIjoidGVzdEB0ZXN0LmNvbSIsInVzZXJfaWQiOiIwVmxrSm8zIn0.BFwveZAtpyGkdkgGuXMivYwVD7zPz8NZVba29P3cX84',
});

const api = new Router({
  categories: new Resource('categories/'),
  category: new Resource('categories/${id}/'),
  shops: new Resource('shops/'),
  shop: new Resource('shops/${id}/'),
  discounts: new Resource('discounts/'),
  discount: new Resource('discounts/${id}/'),
}, {
  apiRoot: '/api/v1/',
  headers: getHeaders,
});

export default api;
