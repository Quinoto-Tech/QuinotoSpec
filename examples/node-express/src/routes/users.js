const express = require('express');

const router = express.Router();

// In-memory store (solo para demo)
const users = [];
let nextId = 1;

router.get('/', (req, res) => {
  res.json(users);
});

router.post('/', (req, res) => {
  const { username, email } = req.body || {};
  if (!username || !email) {
    return res.status(400).json({ error: 'username and email are required' });
  }
  const user = { id: nextId++, username, email };
  users.push(user);
  res.status(201).json(user);
});

router.get('/:id', (req, res) => {
  const user = users.find((u) => u.id === Number(req.params.id));
  if (!user) {
    return res.status(404).json({ error: 'User not found' });
  }
  res.json(user);
});

router.delete('/:id', (req, res) => {
  const index = users.findIndex((u) => u.id === Number(req.params.id));
  if (index === -1) {
    return res.status(404).json({ error: 'User not found' });
  }
  const [removed] = users.splice(index, 1);
  res.json(removed);
});

module.exports = router;
