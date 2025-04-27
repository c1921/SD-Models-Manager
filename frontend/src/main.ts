import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import "flyonui/flyonui";
import Toast from 'vue-toastification';
import 'vue-toastification/dist/index.css';

const app = createApp(App)

// 配置Vue Toastification
const toastOptions = {
  timeout: 2000,
  position: 'top-right',
  closeOnClick: true,
  pauseOnHover: true,
  hideProgressBar: false,
  closeButton: 'button',
  transition: 'Vue-Toastification__fade'
};

app.use(router)
app.use(Toast, toastOptions)
app.mount('#app')
