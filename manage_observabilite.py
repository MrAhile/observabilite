# manage_k8s_observability.py
import subprocess
import yaml
import os
import time

CONFIG_FILE = 'config.yaml'

def load_config():
    """Charge la configuration depuis le fichier config.yaml."""
    try:
        with open(CONFIG_FILE, 'r') as f:
            config = yaml.safe_load(f)
        return config
    except FileNotFoundError:
        print(f"❌ Erreur : Le fichier de configuration '{CONFIG_FILE}' est introuvable.")
        exit(1)
    except yaml.YAMLError as e:
        print(f"❌ Erreur lors de la lecture du fichier de configuration '{CONFIG_FILE}': {e}")
        exit(1)

def run_kubectl_command(command, dry_run=False):
    """Exécute une commande kubectl."""
    print(f"\n🚀 Exécution : {' '.join(command)}")
    if dry_run:
        print("  (👻 Mode Dry-Run : Commande non exécutée)")
        return True, ""

    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        print(result.stdout)
        if result.stderr:
            print(f"⚠️ Erreurs/Avertissements : \n{result.stderr}")
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        print(f"❌ Erreur lors de l'exécution de la commande : {e}")
        print(f"Sortie standard : \n{e.stdout}")
        print(f"Sortie d'erreur : \n{e.stderr}")
        return False, e.stderr
    except FileNotFoundError:
        print("❌ Erreur : 'kubectl' n'est pas trouvé. Assurez-vous qu'il est installé et dans votre PATH.")
        return False, "kubectl not found"

def start_resources(config, dry_run=False):
    """Démarre toutes les ressources Kubernetes."""
    print("--- ▶️ Démarrage des ressources Kubernetes ---")
    namespace = config['namespace']
    resource_dir = config['resource_directory']
    resources = config['resources']

    # Créer le namespace en premier
    ns_file = os.path.join(resource_dir, resources[0]) # Assumons que le namespace est le premier fichier
    print(f"✨ Application du namespace : {ns_file}")
    success, _ = run_kubectl_command(['kubectl', 'apply', '-f', ns_file], dry_run)
    if not success and not dry_run:
        print(f"❌ Échec de la création du namespace {namespace}. Abort.")
        return False
    time.sleep(2) # Laisser le temps au namespace de se propager (utile en mode réel)

    for resource_file in resources[1:]:
        file_path = os.path.join(resource_dir, resource_file)
        if not os.path.exists(file_path):
            print(f"⚠️ Avertissement : Le fichier '{file_path}' est introuvable. Ignoré.")
            continue
        print(f"🚀 Application de {resource_file}...")
        success, _ = run_kubectl_command(['kubectl', 'apply', '-f', file_path, '-n', namespace], dry_run)
        if not success and not dry_run:
            print(f"❌ Erreur lors de l'application de {resource_file}. La suite du déploiement pourrait être affectée.")
    print("--- ✅ Démarrage des ressources terminé ---")
    return True

def stop_resources(config, dry_run=False):
    """Arrête toutes les ressources Kubernetes."""
    print("--- 🛑 Arrêt des ressources Kubernetes ---")
    namespace = config['namespace']
    resource_dir = config['resource_directory']
    resources = config['resources']

    # Supprimer les ressources dans l'ordre inverse
    for resource_file in reversed(resources):
        if 'namespace' in resource_file.lower():
             continue

        file_path = os.path.join(resource_dir, resource_file)
        if not os.path.exists(file_path):
            print(f"⚠️ Avertissement : Le fichier '{file_path}' est introuvable. Ignoré.")
            continue
        print(f"🗑️ Suppression de {resource_file}...")
        success, _ = run_kubectl_command(['kubectl', 'delete', '-f', file_path, '-n', namespace], dry_run)
        if not success and not dry_run:
            print(f"❌ Erreur lors de la suppression de {resource_file}. Continuer avec les autres ressources.")

    # Supprimer le namespace en dernier
    ns_file = os.path.join(resource_dir, resources[0])
    print(f"🔥 Suppression du namespace : {namespace}")
    success, _ = run_kubectl_command(['kubectl', 'delete', '-f', ns_file], dry_run)
    if not success and not dry_run:
        print(f"❌ Échec de la suppression du namespace {namespace}. Vous devrez peut-être le supprimer manuellement.")
    print("--- ✅ Arrêt des ressources terminé ---")
    return True

def get_pod_status(config):
    """Affiche le statut des pods dans le namespace."""
    print("--- 🔍 Statut des Pods Kubernetes ---")
    namespace = config['namespace']
    success, output = run_kubectl_command(['kubectl', 'get', 'pods', '-n', namespace])
    if success:
        print("\n" + output)
    print("--- ✅ Affichage du statut des Pods terminé ---")

def display_menu():
    """Affiche le menu des options."""
    print("\n--- 🔧 Gestion de l'Observabilité Kubernetes ---")
    print("1. ▶️ Démarrer toutes les ressources")
    print("2. 🛑 Arrêter toutes les ressources")
    print("3. 🔍 Voir le statut des Pods")
    print("4. 👻 Démarrer les ressources (Dry-Run)")
    print("5. 👻 Arrêter les ressources (Dry-Run)")
    print("6. 🚪 Quitter")
    print("------------------------------------------")

def main():
    config = load_config()

    while True:
        display_menu()
        choice = input("👉 Choisissez une option : ")

        if choice == '1':
            start_resources(config)
            get_pod_status(config)
        elif choice == '2':
            stop_resources(config)
            get_pod_status(config)
        elif choice == '3':
            get_pod_status(config)
        elif choice == '4':
            start_resources(config, dry_run=True)
        elif choice == '5':
            stop_resources(config, dry_run=True)
        elif choice == '6':
            print("👋 Quitting...")
            break
        else:
            print("⛔ Option invalide. Veuillez réessayer.")

if __name__ == "__main__":
    main()