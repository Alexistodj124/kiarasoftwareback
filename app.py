from flask import Flask, jsonify, request
from config import Config
from models import db, Producto, Servicio, Cliente, Orden, OrdenItem, Usuario, Empleada
from flask_migrate import Migrate
from datetime import datetime


migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    migrate.init_app(app, db)

    @app.route("/")
    def index():
        return jsonify({"message": "API funcionando"}

    # ---------- CRUD PRODUCTOS ----------

    @app.route("/productos", methods=["GET"])
    def listar_productos():
        productos = Producto.query.all()
        data = []
        for p in productos:
            data.append({
                "id": p.id,
                "marca": p.marca,
                "descripcion": p.descripcion,
                "categoria": p.categoria,
                "costo": float(p.costo),
                "precio": float(p.precio),
                "cantidad": p.cantidad,
                "imagen": p.imagen,
            })
        return jsonify(data)

    @app.route("/productos/<int:producto_id>", methods=["GET"])
    def obtener_producto(producto_id):
        p = Producto.query.get_or_404(producto_id)
        return jsonify({
            "id": p.id,
            "marca": p.marca,
            "descripcion": p.descripcion,
            "categoria": p.categoria,
            "costo": float(p.costo),
            "precio": float(p.precio),
            "cantidad": p.cantidad,
            "imagen": p.imagen,
        })

    @app.route("/productos", methods=["POST"])
    def crear_producto():
        data = request.get_json()

        p = Producto(
            marca=data["marca"],
            descripcion=data["descripcion"],
            categoria=data["categoria"],
            costo=data["costo"],
            precio=data["precio"],
            cantidad=data.get("cantidad", 0),
            imagen=data.get("imagen"),
        )

        db.session.add(p)
        db.session.commit()

        return jsonify({"id": p.id}), 201

    @app.route("/productos/<int:producto_id>", methods=["PUT", "PATCH"])
    def actualizar_producto(producto_id):
        p = Producto.query.get_or_404(producto_id)
        data = request.get_json()

        p.marca = data.get("marca", p.marca)
        p.descripcion = data.get("descripcion", p.descripcion)
        p.categoria = data.get("categoria", p.categoria)
        if "costo" in data:
            p.costo = data["costo"]
        if "precio" in data:
            p.precio = data["precio"]
        if "cantidad" in data:
            p.cantidad = data["cantidad"]
        if "imagen" in data:
            p.imagen = data["imagen"]

        db.session.commit()

        return jsonify({"message": "Producto actualizado"})

    @app.route("/productos/<int:producto_id>", methods=["DELETE"])
    def eliminar_producto(producto_id):
        p = Producto.query.get_or_404(producto_id)
        db.session.delete(p)
        db.session.commit()
        return jsonify({"message": "Producto eliminado"})
    
        # ---------- CRUD SERVICIOS ----------

    @app.route("/servicios", methods=["GET"])
    def listar_servicios():
        servicios = Servicio.query.all()
        data = []
        for s in servicios:
            data.append({
                "id": s.id,
                "descripcion": s.descripcion,
                "categoria": s.categoria,
                "costo": float(s.costo),
                "precio": float(s.precio),
                "imagen": s.imagen,
            })
        return jsonify(data)

    @app.route("/servicios/<int:servicio_id>", methods=["GET"])
    def obtener_servicio(servicio_id):
        s = Servicio.query.get_or_404(servicio_id)
        return jsonify({
            "id": s.id,
            "descripcion": s.descripcion,
            "categoria": s.categoria,
            "costo": float(s.costo),
            "precio": float(s.precio),
            "imagen": s.imagen,
        })

    @app.route("/servicios", methods=["POST"])
    def crear_servicio():
        data = request.get_json()

        # Aquí podrías agregar validaciones básicas si quieres
        s = Servicio(
            descripcion=data["descripcion"],
            categoria=data["categoria"],
            costo=data["costo"],
            precio=data["precio"],
            imagen=data.get("imagen"),
        )

        db.session.add(s)
        db.session.commit()

        return jsonify({"id": s.id}), 201

    @app.route("/servicios/<int:servicio_id>", methods=["PUT", "PATCH"])
    def actualizar_servicio(servicio_id):
        s = Servicio.query.get_or_404(servicio_id)
        data = request.get_json()

        s.descripcion = data.get("descripcion", s.descripcion)
        s.categoria = data.get("categoria", s.categoria)

        if "costo" in data:
            s.costo = data["costo"]
        if "precio" in data:
            s.precio = data["precio"]
        if "imagen" in data:
            s.imagen = data["imagen"]

        db.session.commit()

        return jsonify({"message": "Servicio actualizado"})

    @app.route("/servicios/<int:servicio_id>", methods=["DELETE"])
    def eliminar_servicio(servicio_id):
        s = Servicio.query.get_or_404(servicio_id)
        db.session.delete(s)
        db.session.commit()
        return jsonify({"message": "Servicio eliminado"})


    def parse_iso_datetime(value: str) -> datetime:
        """
        Intenta parsear un string ISO 8601. Si falla, devuelve ahora.
        Soporta 'Z' al final (UTC).
        """
        if not value:
            return datetime.utcnow()
        try:
            # Reemplazamos Z por +00:00 para que fromisoformat lo acepte
            value = value.replace("Z", "+00:00")
            return datetime.fromisoformat(value)
        except Exception:
            return datetime.utcnow()


    def orden_to_dict(orden: Orden):
        return {
            "id": orden.id,
            "codigo": orden.codigo,
            "fecha": orden.fecha.isoformat(),
            "empleada": {
                "id": orden.empleada.id,
                "nombre": orden.empleada.nombre,
                "telefono": orden.empleada.telefono,
            },
            "cliente": {
                "id": orden.cliente.id,
                "nombre": orden.cliente.nombre,
                "telefono": orden.cliente.telefono,
            },
            "items": [
                {
                    "id": item.id,
                    "tipo": item.tipo,
                    "producto_id": item.producto_id,
                    "servicio_id": item.servicio_id,
                    "cantidad": item.cantidad,
                    "precio_unitario": float(item.precio_unitario),
                    "producto": {
                        "id": item.producto.id,
                        "marca": item.producto.marca,
                        "descripcion": item.producto.descripcion,
                    } if item.producto else None,
                    "servicio": {
                        "id": item.servicio.id,
                        "descripcion": item.servicio.descripcion,
                    } if item.servicio else None,
                }
                for item in orden.items
            ],
        }


        # ---------- CRUD ORDENES ----------

    @app.route("/ordenes", methods=["GET"])
    def listar_ordenes():
        ordenes = Orden.query.order_by(Orden.fecha.desc()).all()
        data = [orden_to_dict(o) for o in ordenes]
        return jsonify(data)

    @app.route("/ordenes/<int:orden_id>", methods=["GET"])
    def obtener_orden(orden_id):
        orden = Orden.query.get_or_404(orden_id)
        return jsonify(orden_to_dict(orden))

    @app.route("/ordenes", methods=["POST"])
    def crear_orden():
        """
        Espera un JSON tipo:

        {
          "codigo": "ORD-001",
          "fecha": "2025-11-10T10:10:00Z",   // opcional
          "empleada": "Ana",
          "cliente": {
            "id": 1                      // OPCIÓN 1: cliente existente
          }
          // O bien:
          // "cliente": {
          //   "nombre": "Ana López",     // OPCIÓN 2: crear/buscar por datos
          //   "telefono": "+502 5555 1111"
          // },
          "items": [
            { "tipo": "producto", "producto_id": 1, "cantidad": 2, "precio_unitario": 250 },
            { "tipo": "servicio", "servicio_id": 3, "cantidad": 1, "precio_unitario": 400 }
          ]
        }
        """
        data = request.get_json()

        # 1) Cliente
        cliente_data = data.get("cliente")
        if not cliente_data:
            return jsonify({"error": "cliente es requerido"}), 400

        cliente = None

        # Si viene cliente.id, usamos cliente existente
        if "id" in cliente_data:
            cliente = Cliente.query.get(cliente_data["id"])
            if not cliente:
                return jsonify({"error": "cliente con ese id no existe"}), 400
        else:
            # Buscamos por telefono (y/o nombre). Si no existe, lo creamos.
            nombre = cliente_data.get("nombre")
            telefono = cliente_data.get("telefono")

            if not nombre or not telefono:
                return jsonify({"error": "cliente requiere nombre y telefono"}), 400

            cliente = Cliente.query.filter_by(telefono=telefono).first()
            if not cliente:
                cliente = Cliente(nombre=nombre, telefono=telefono)
                db.session.add(cliente)
                db.session.flush()  # para tener cliente.id antes de crear la orden

    # ----- EMPLEADA -----
        empleada_data = data.get("empleada")
        if not empleada_data:
            return jsonify({"error": "empleada es requerida"}), 400

        empleada = None

        # Si viene empleada.id, usamos empleada existente
        if "id" in empleada_data:
            empleada = Empleada.query.get(empleada_data["id"])
            if not empleada:
                return jsonify({"error": "empleada con ese id no existe"}), 400
        else:
            nombre_emp = empleada_data.get("nombre")
            tel_emp = empleada_data.get("telefono")

            if not nombre_emp:
                return jsonify({"error": "empleada requiere al menos nombre"}), 400

            # Puedes decidir si buscas por nombre+telefono o siempre creas nueva
            # Aquí ejemplo: buscar por nombre+telefono
            q = Empleada.query.filter_by(nombre=nombre_emp)
            if tel_emp:
                q = q.filter_by(telefono=tel_emp)
            empleada = q.first()

            if not empleada:
                empleada = Empleada(nombre=nombre_emp, telefono=tel_emp)
                db.session.add(empleada)
                db.session.flush()
        # 2) Orden
        codigo = data.get("codigo")
        if not codigo:
            return jsonify({"error": "codigo de orden es requerido"}), 400

        fecha_str = data.get("fecha")
        fecha = parse_iso_datetime(fecha_str) if fecha_str else datetime.utcnow()

        orden = Orden(
            codigo=codigo,
            fecha=fecha,
            empleada=empleada,
            cliente=cliente
        )
        db.session.add(orden)
        db.session.flush()  # para tener orden.id

        # 3) Items
        items_data = data.get("items", [])
        if not items_data:
            return jsonify({"error": "debe incluir al menos un item en 'items'"}), 400

        for item_data in items_data:
            tipo = item_data.get("tipo")
            cantidad = item_data.get("cantidad", 1)
            precio_unitario = item_data.get("precio_unitario")

            if tipo not in ("producto", "servicio"):
                return jsonify({"error": "tipo de item debe ser 'producto' o 'servicio'"}), 400

            if precio_unitario is None:
                return jsonify({"error": "precio_unitario es requerido en cada item"}), 400

            if tipo == "producto":
                producto_id = item_data.get("producto_id")
                if not producto_id:
                    return jsonify({"error": "producto_id es requerido cuando tipo='producto'"}), 400
                producto = Producto.query.get(producto_id)
                if not producto:
                    return jsonify({"error": f"producto {producto_id} no existe"}), 400

                orden_item = OrdenItem(
                    orden=orden,
                    tipo="producto",
                    producto=producto,
                    cantidad=cantidad,
                    precio_unitario=precio_unitario,
                )
            else:  # servicio
                servicio_id = item_data.get("servicio_id")
                if not servicio_id:
                    return jsonify({"error": "servicio_id es requerido cuando tipo='servicio'"}), 400
                servicio = Servicio.query.get(servicio_id)
                if not servicio:
                    return jsonify({"error": f"servicio {servicio_id} no existe"}), 400

                orden_item = OrdenItem(
                    orden=orden,
                    tipo="servicio",
                    servicio=servicio,
                    cantidad=cantidad,
                    precio_unitario=precio_unitario,
                )

            db.session.add(orden_item)

        db.session.commit()

        return jsonify(orden_to_dict(orden)), 201

    @app.route("/ordenes/<int:orden_id>", methods=["PUT", "PATCH"])
    def actualizar_orden(orden_id):
        """
        Permite actualizar:
        - codigo
        - fecha
        - empleada
        - cliente (solo por id)
        - items (si se envía 'items', se reemplazan todos los items)
        """
        orden = Orden.query.get_or_404(orden_id)
        data = request.get_json()

        if "codigo" in data:
            orden.codigo = data["codigo"]

        if "fecha" in data:
            orden.fecha = parse_iso_datetime(data["fecha"])

        if "empleada" in data:
            orden.empleada = data["empleada"]

        # Cliente (solo permitimos cambiar cliente por id para simplificar)
        if "cliente_id" in data:
            cliente = Cliente.query.get(data["cliente_id"])
            if not cliente:
                return jsonify({"error": "cliente_id no válido"}), 400
            orden.cliente = cliente

        # Reemplazar items si viene "items"
        if "items" in data:
            # Borramos items actuales
            for item in list(orden.items):
                db.session.delete(item)
            db.session.flush()

            items_data = data["items"]
            for item_data in items_data:
                tipo = item_data.get("tipo")
                cantidad = item_data.get("cantidad", 1)
                precio_unitario = item_data.get("precio_unitario")

                if tipo not in ("producto", "servicio"):
                    return jsonify({"error": "tipo de item debe ser 'producto' o 'servicio'"}), 400

                if precio_unitario is None:
                    return jsonify({"error": "precio_unitario es requerido en cada item"}), 400

                if tipo == "producto":
                    producto_id = item_data.get("producto_id")
                    producto = Producto.query.get(producto_id)
                    if not producto:
                        return jsonify({"error": f"producto {producto_id} no existe"}), 400
                    orden_item = OrdenItem(
                        orden=orden,
                        tipo="producto",
                        producto=producto,
                        cantidad=cantidad,
                        precio_unitario=precio_unitario,
                    )
                else:
                    servicio_id = item_data.get("servicio_id")
                    servicio = Servicio.query.get(servicio_id)
                    if not servicio:
                        return jsonify({"error": f"servicio {servicio_id} no existe"}), 400
                    orden_item = OrdenItem(
                        orden=orden,
                        tipo="servicio",
                        servicio=servicio,
                        cantidad=cantidad,
                        precio_unitario=precio_unitario,
                    )

                db.session.add(orden_item)

        db.session.commit()
        return jsonify(orden_to_dict(orden))

    @app.route("/ordenes/<int:orden_id>", methods=["DELETE"])
    def eliminar_orden(orden_id):
        orden = Orden.query.get_or_404(orden_id)
        db.session.delete(orden)
        db.session.commit()
        return jsonify({"message": "Orden eliminada"})

        # ---------- CRUD USUARIOS ----------

    @app.route("/usuarios", methods=["GET"])
    def listar_usuarios():
        """
        Lista todos los usuarios.
        No devolvemos password_hash por seguridad.
        """
        usuarios = Usuario.query.all()
        data = [
            {
                "id": u.id,
                "username": u.username,
                "is_admin": u.is_admin,
                "creado_en": u.creado_en.isoformat(),
            }
            for u in usuarios
        ]
        return jsonify(data)

    @app.route("/usuarios/<int:usuario_id>", methods=["GET"])
    def obtener_usuario(usuario_id):
        """
        Retorna un usuario específico.
        """
        u = Usuario.query.get_or_404(usuario_id)
        return jsonify({
            "id": u.id,
            "username": u.username,
            "is_admin": u.is_admin,
            "creado_en": u.creado_en.isoformat(),
        })

    @app.route("/usuarios", methods=["POST"])
    def crear_usuario():
        """
        Crea un usuario nuevo.

        Espera JSON:
        {
        "username": "ana",
        "password": "mi_contrasena_segura",
        "is_admin": true   // opcional, default false
        }
        """
        data = request.get_json()

        username = data.get("username")
        password = data.get("password")
        is_admin = data.get("is_admin", False)

        if not username or not password:
            return jsonify({"error": "username y password son requeridos"}), 400

        # Verificar que no exista ya
        if Usuario.query.filter_by(username=username).first():
            return jsonify({"error": "username ya existe"}), 400

        usuario = Usuario(
            username=username,
            is_admin=is_admin
        )
        usuario.set_password(password)

        db.session.add(usuario)
        db.session.commit()

        return jsonify({
            "id": usuario.id,
            "username": usuario.username,
            "is_admin": usuario.is_admin,
            "creado_en": usuario.creado_en.isoformat(),
        }), 201

    @app.route("/usuarios/<int:usuario_id>", methods=["PUT", "PATCH"])
    def actualizar_usuario(usuario_id):
        """
        Actualiza datos del usuario.

        Puedes mandar cualquiera de:
        {
        "username": "nuevo_nombre",
        "password": "nueva_contrasena",
        "is_admin": true/false
        }
        """
        usuario = Usuario.query.get_or_404(usuario_id)
        data = request.get_json()

        if "username" in data:
            nuevo_username = data["username"]
            if nuevo_username != usuario.username:
                # Revisar que no se repita
                if Usuario.query.filter_by(username=nuevo_username).first():
                    return jsonify({"error": "username ya existe"}), 400
                usuario.username = nuevo_username

        if "password" in data and data["password"]:
            usuario.set_password(data["password"])

        if "is_admin" in data:
            usuario.is_admin = bool(data["is_admin"])

        db.session.commit()

        return jsonify({
            "id": usuario.id,
            "username": usuario.username,
            "is_admin": usuario.is_admin,
            "creado_en": usuario.creado_en.isoformat(),
        })

    @app.route("/usuarios/<int:usuario_id>", methods=["DELETE"])
    def eliminar_usuario(usuario_id):
        """
        Elimina un usuario.
        (Más adelante puedes agregar lógica para no borrar el último admin, etc.)
        """
        usuario = Usuario.query.get_or_404(usuario_id)
        db.session.delete(usuario)
        db.session.commit()
        return jsonify({"message": "Usuario eliminado"})

    @app.route("/auth/login", methods=["POST"])
    def login():
        """
        Login básico.

        Espera JSON:
        {
        "username": "ana",
        "password": "mi_contrasena"
        }

        Responde 200 si las credenciales son correctas,
        401 si no.
        """
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        if not username or not password:
            return jsonify({"error": "username y password son requeridos"}), 400

        usuario = Usuario.query.filter_by(username=username).first()
        if not usuario or not usuario.check_password(password):
            return jsonify({"error": "credenciales inválidas"}), 401

        # Más adelante aquí podrías devolver un JWT o sesión.
        return jsonify({
            "id": usuario.id,
            "username": usuario.username,
            "is_admin": usuario.is_admin
        })

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
