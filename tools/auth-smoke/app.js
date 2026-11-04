import { initializeApp } from "https://www.gstatic.com/firebasejs/11.10.0/firebase-app.js";
import { getAuth, GoogleAuthProvider, signInWithPopup, signOut, onAuthStateChanged } from "https://www.gstatic.com/firebasejs/11.10.0/firebase-auth.js";
import { firebaseConfig } from "./firebase-config.local.js";

const PROJECT = "proyectopersonal-480420";
const status = document.getElementById("state");
const confirm = document.getElementById("dedicated");
const login = document.getElementById("login");
const logout = document.getElementById("logout");
const identity = document.getElementById("identity");
const result = document.getElementById("result");
const copyUid = document.getElementById("copyUid");

if (location.hostname !== "localhost") {
  throw new Error("This smoke test must only run on http://localhost. Do not host publicly.");
}
if (firebaseConfig.projectId !== PROJECT ||
    firebaseConfig.authDomain !== PROJECT + ".firebaseapp.com") {
  throw new Error("Unexpected Firebase project/authDomain. Check local configuration.");
}
const auth = getAuth(initializeApp(firebaseConfig));
auth.languageCode = "es";

let currentUid = null;
let busy = false;
function refreshControls() {
  login.disabled = busy || !confirm.checked || !!auth.currentUser;
  logout.disabled = busy || !auth.currentUser;
}
confirm.addEventListener("change", refreshControls);
onAuthStateChanged(auth, user => {
  currentUid = user?.uid ?? null;
  identity.hidden = !user;
  if (user) {
    result.textContent = "Correo: " + (user.email ?? "(sin correo)") +
      "\nFirebase UID: " + user.uid +
      "\nProveedor: " + (user.providerData[0]?.providerId ?? "(desconocido)");
    status.textContent = "Sesión iniciada. Confirma en Firebase Authentication que se creó el usuario correcto.";
  } else {
    result.textContent = "";
    status.textContent = "Sin sesión. Selecciona la cuenta dedicada al iniciar sesión.";
  }
  refreshControls();
}, error => {
  status.textContent = "Error al verificar la sesión: " + (error.code ?? "desconocido");
});
login.addEventListener("click", async () => {
  if (!confirm.checked || busy) return;
  busy = true;
  refreshControls();
  try {
    const provider = new GoogleAuthProvider();
    provider.setCustomParameters({ prompt: "select_account" });
    const credential = await signInWithPopup(auth, provider);
    if (credential.user.providerData.every(x => x.providerId !== "google.com")) {
      await signOut(auth);
      throw new Error("El inicio de sesión no usó el proveedor Google.");
    }
  } catch (error) {
    status.textContent = "No se pudo iniciar sesión: " + (error.code ?? error.message ?? "error");
  } finally {
    busy = false;
    refreshControls();
  }
});
logout.addEventListener("click", async () => {
  busy = true;
  refreshControls();
  try { await signOut(auth); }
  catch (error) { status.textContent = "Error al cerrar sesión: " + (error.code ?? "desconocido"); }
  finally { busy = false; refreshControls(); }
});
copyUid.addEventListener("click", async () => {
  if (!currentUid) return;
  try {
    await navigator.clipboard.writeText(currentUid);
    status.textContent = "UID copiado. No compartas tokens de acceso.";
  } catch {
    status.textContent = "Selecciona y copia el UID que aparece en la página.";
  }
});
