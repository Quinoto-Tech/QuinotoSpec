const request = require('supertest');
const app = require('../src/index');

describe('Health endpoints', () => {
  test('GET / returns status ok', async () => {
    const res = await request(app).get('/');
    expect(res.status).toBe(200);
    expect(res.body.status).toBe('ok');
  });

  test('GET /health returns healthy', async () => {
    const res = await request(app).get('/health');
    expect(res.status).toBe(200);
    expect(res.body.status).toBe('healthy');
  });
});

describe('Users endpoints', () => {
  test('POST /users creates a user', async () => {
    const res = await request(app)
      .post('/users')
      .send({ username: 'testuser', email: 'test@example.com' });
    expect(res.status).toBe(201);
    expect(res.body.username).toBe('testuser');
    expect(res.body).toHaveProperty('id');
  });

  test('GET /users lists users', async () => {
    const res = await request(app).get('/users');
    expect(res.status).toBe(200);
    expect(Array.isArray(res.body)).toBe(true);
  });

  test('GET /users/:id returns 404 for unknown id', async () => {
    const res = await request(app).get('/users/999');
    expect(res.status).toBe(404);
  });

  test('POST /users without email returns 400', async () => {
    const res = await request(app).post('/users').send({ username: 'x' });
    expect(res.status).toBe(400);
  });
});
