import js from "@eslint/js";
import htmlPlugin from "eslint-plugin-html";
import globals from "globals";

export default [
  // Base config
  js.configs.recommended,

  // Global config (applies everywhere unless overridden)
  {
    languageOptions: {
      sourceType: "module",
      ecmaVersion: 11,
      globals: {
        ...globals.browser, // adds document, window, etc.
        ...globals.jquery   // adds $, jQuery, etc.
      }
    },
    rules: {
      "no-unused-vars": ["error", { "vars": "all", "args": "none", "ignoreRestSiblings": false }],
      "prefer-const": ["error", { "destructuring": "any", "ignoreReadBeforeAssign": false }],
      "no-var": "error",
      "semi": "error"
    }
  },

  // Extra config for *.html
  {
    files: ["**/*.html"],
    plugins: {
      html: htmlPlugin
    }
  }
];
