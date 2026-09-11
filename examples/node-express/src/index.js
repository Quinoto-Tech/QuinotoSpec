const express = require('express');
const usersRouter = require('./routes/users');

const app = express();
app.use(express.json());

app.get('/', (req, res) => {
  res.json({ status: 'ok', message: 'QuinotoSpec Example API' });
});

app.get('/health', (req, res) => {
  res.json({ status: 'healthy' });
});

app.use('/users', usersRouter);

module.exports = app;

if (require.main === module) {
  const PORT = process.env.PORT || 3000;
  app.listen(PORT, () => {
    console.log(`QuinotoSpec Example API listening on port ${PORT}`);
  });
}
