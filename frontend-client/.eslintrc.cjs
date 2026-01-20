module.exports = {
  root: true,
  env: {
    browser: true,
    es2022: true,
  },
  parserOptions: {
    ecmaVersion: 2022,
    sourceType: 'module',
    ecmaFeatures: {
      jsx: true,
    },
  },
  settings: {
    react: {
      version: 'detect',
    },
  },
  plugins: ['react', 'react-hooks', 'unused-imports'],
  extends: ['eslint:recommended', 'plugin:react/recommended', 'plugin:react-hooks/recommended'],
  rules: {
    // App is JS/JSX only; avoid forcing prop-types in this codebase.
    'react/prop-types': 'off',

    // React 17+ JSX transform
    'react/react-in-jsx-scope': 'off',

    // react-three-fiber / three.js components use non-DOM props like `args`, `intensity`, etc.
    'react/no-unknown-property': 'off',

    // Legal/docs pages include lots of apostrophes; keep lint non-blocking.
    'react/no-unescaped-entities': 'off',

    // Reduce noise from unused icon imports, etc.
    'unused-imports/no-unused-imports': 'warn',
    'unused-imports/no-unused-vars': ['warn', { argsIgnorePattern: '^_', varsIgnorePattern: '^_' }],
    'no-unused-vars': 'off',
    'no-console': 'off',

    // Allow intentionally empty catch blocks (common for best-effort UI actions).
    'no-empty': ['error', { allowEmptyCatch: true }],
  },
};
