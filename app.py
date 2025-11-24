from flask import Flask, jsonify, request
from config import Config
from models import db, Producto, Servicio, Cliente, Orden, OrdenItem, Usuario, Empleada, CategoriaProducto, CategoriaServicio, MarcaProducto
from flask_migrate import Migrate
from datetime import datetime
from flask_cors import CORS
from datetime import datetime



migrate = Migrate()


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Habilitar CORS para el front (localhost:5173)
    CORS(app, resources={r"/*": {"origins": "*"}})
    # Si quieres permitir cualquier origen durante desarrollo:
    # CORS(app)

    db.init_app(app)
    migrate.init_app(app, db)

    @app.route("/")
    def index():
        return jsonify({"message": "API funcionando"})

    # ---------- CRUD PRODUCTOS ----------

    @app.route("/productos", methods=["GET"])
    def listar_productos():
        productos = Producto.query.all()
        data = []
        for p in productos:
            data.append({
                "id": p.id,
                "marca": p.marca.nombre if p.marca else None,
                "marca_id": p.marca.id if p.marca else None,
                "descripcion": p.descripcion,
                "categoria": p.categoria.nombre if p.categoria else None,
                "categoria_id": p.categoria.id if p.categoria else None,
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
            "marca": p.marca.nombre if p.marca else None,
            "marca_id": p.marca.id if p.marca else None,
            "descripcion": p.descripcion,
            "categoria": p.categoria.nombre if p.categoria else None,
            "categoria_id": p.categoria.id if p.categoria else None,
            "costo": float(p.costo),
            "precio": float(p.precio),
            "cantidad": p.cantidad,
            "imagen": p.imagen,
        })


    @app.route("/productos", methods=["POST"])
    def crear_producto():
        data = request.get_json()

        # ===== MARCA =====
        marca = None

        # 1) Si viene marca_id, usamos el ID
        marca_id = data.get("marca_id")
        if marca_id is not None:
            marca = MarcaProducto.query.get(marca_id)
            if not marca:
                return jsonify({"error": "marca_id inválido"}), 400
        else:
            # 2) Compatibilidad: si viene 'marca' como nombre (string)
            marca_nombre = data.get("marca")
            if marca_nombre:
                marca = MarcaProducto.query.filter_by(nombre=str(marca_nombre)).first()
                if not marca:
                    marca = MarcaProducto(nombre=str(marca_nombre))
                    db.session.add(marca)
                    db.session.flush()

        # ===== CATEGORÍA =====
        categoria = None

        categoria_id = data.get("categoria_id")
        if categoria_id is not None:
            categoria = CategoriaProducto.query.get(categoria_id)
            if not categoria:
                return jsonify({"error": "categoria_id inválido"}), 400
        else:
            categoria_nombre = data.get("categoria")
            if categoria_nombre:
                categoria = CategoriaProducto.query.filter_by(nombre=str(categoria_nombre)).first()
                if not categoria:
                    categoria = CategoriaProducto(nombre=str(categoria_nombre))
                    db.session.add(categoria)
                    db.session.flush()

        # ===== PRODUCTO =====
        p = Producto(
            marca=marca,
            categoria=categoria,
            descripcion=data["descripcion"],
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

        if "descripcion" in data:
            p.descripcion = data["descripcion"]

        # 🔹 Marca
        if "marca" in data:
            marca_nombre = data.get("marca")
            if marca_nombre:
                m = MarcaProducto.query.filter_by(nombre=marca_nombre).first()
                if not m:
                    m = MarcaProducto(nombre=marca_nombre)
                    db.session.add(m)
                    db.session.flush()
                p.marca = m
            else:
                p.marca = None

        # 🔹 Categoría (ya la teníamos)
        if "categoria" in data:
            categoria_nombre = data.get("categoria")
            if categoria_nombre:
                cat = CategoriaProducto.query.filter_by(nombre=categoria_nombre).first()
                if not cat:
                    cat = CategoriaProducto(nombre=categoria_nombre)
                    db.session.add(cat)
                    db.session.flush()
                p.categoria = cat
            else:
                p.categoria = None

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
                "categoria": s.categoria.nombre if s.categoria else None,
                "categoria_id": s.categoria.id if s.categoria else None,
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
            "categoria": s.categoria.nombre if s.categoria else None,
            "categoria_id": s.categoria.id if s.categoria else None,
            "costo": float(s.costo),
            "precio": float(s.precio),
            "imagen": s.imagen,
        })


    @app.route("/servicios", methods=["POST"])
    def crear_servicio():
        data = request.get_json()

        # ===== CATEGORÍA =====
        categoria = None

        categoria_id = data.get("categoria_id")
        if categoria_id is not None:
            categoria = CategoriaServicio.query.get(categoria_id)
            if not categoria:
                return jsonify({"error": "categoria_id inválido"}), 400
        else:
            categoria_nombre = data.get("categoria")
            if categoria_nombre:
                categoria = CategoriaServicio.query.filter_by(nombre=str(categoria_nombre)).first()
                if not categoria:
                    categoria = CategoriaServicio(nombre=str(categoria_nombre))
                    db.session.add(categoria)
                    db.session.flush()

        s = Servicio(
            descripcion=data["descripcion"],
            costo=data["costo"],
            precio=data["precio"],
            imagen=data.get("imagen"),
            categoria=categoria,
        )

        db.session.add(s)
        db.session.commit()

        return jsonify({"id": s.id}), 201


    @app.route("/servicios/<int:servicio_id>", methods=["PUT", "PATCH"])
    def actualizar_servicio(servicio_id):
        s = Servicio.query.get_or_404(servicio_id)
        data = request.get_json()

        s.descripcion = data.get("descripcion", s.descripcion)

        if "categoria" in data:
            categoria_nombre = data.get("categoria")
            if categoria_nombre:
                cat = CategoriaServicio.query.filter_by(nombre=categoria_nombre).first()
                if not cat:
                    cat = CategoriaServicio(nombre=categoria_nombre)
                    db.session.add(cat)
                    db.session.flush()
                s.categoria = cat
            else:
                s.categoria = None

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
        

    def producto_to_dict(p: Producto):
        if p is None:
            return None
        return {
            "id": p.id,
            "descripcion": p.descripcion,
            "precio": float(p.precio),
            "categoria_id": p.categoria_id,
            "marca_id": p.marca_id,
        }

    def servicio_to_dict(s: Servicio):
        if s is None:
            return None
        return {
            "id": s.id,
            "descripcion": s.descripcion,
            "precio": float(s.precio),
            "categoria_id": s.categoria_id,
        }


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
                    "producto": producto_to_dict(item.producto) if item.tipo == "producto" else None,
                    "servicio": servicio_to_dict(item.servicio) if item.tipo == "servicio" else None,
                }
                for item in orden.items
            ],
        }
    from datetime import datetime

    def parse_iso_datetime(value: str) -> datetime:
        """
        Convierte una cadena ISO 8601 a datetime.
        Acepta 'Z' al final como UTC.
        """
        if not value:
            return None
        # si termina en 'Z', lo cambiamos a +00:00
        if value.endswith("Z"):
            value = value[:-1] + "+00:00"
        return datetime.fromisoformat(value)



        # ---------- CRUD ORDENES ----------

    @app.route("/ordenes", methods=["GET"])
    def listar_ordenes():
        """
        Lista órdenes, opcionalmente filtradas por rango de fechas.

        Query params:
        - inicio: fecha/hora ISO 8601 (ej: 2025-11-01T00:00:00Z)
        - fin:    fecha/hora ISO 8601 (ej: 2025-11-30T23:59:59Z)

        Ejemplos:
        GET /ordenes
        GET /ordenes?inicio=2025-11-01T00:00:00Z&fin=2025-11-30T23:59:59Z
        """
        inicio_str = request.args.get("inicio")
        fin_str = request.args.get("fin")

        query = Orden.query

        # Filtro fecha inicio
        if inicio_str:
            try:
                inicio = parse_iso_datetime(inicio_str)
            except Exception:
                return jsonify({"error": "parametro 'inicio' debe estar en formato ISO 8601"}), 400
            query = query.filter(Orden.fecha >= inicio)

        # Filtro fecha fin
        if fin_str:
            try:
                fin = parse_iso_datetime(fin_str)
            except Exception:
                return jsonify({"error": "parametro 'fin' debe estar en formato ISO 8601"}), 400
            query = query.filter(Orden.fecha <= fin)

        ordenes = query.order_by(Orden.fecha.desc()).all()
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

            # Empleada (solo cambiar por id para simplificar)
        if "empleada_id" in data:
            empleada = Empleada.query.get(data["empleada_id"])
            if not empleada:
                return jsonify({"error": "empleada_id no válido"}), 400
            orden.empleada = empleada


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
    
    # ---------- CRUD CATEGORIAS PRODUCTOS ----------

    @app.route("/categorias-productos", methods=["GET"])
    def listar_categorias_productos():
        categorias = CategoriaProducto.query.order_by(CategoriaProducto.nombre).all()
        return jsonify([
            {
                "id": c.id,
                "nombre": c.nombre,
                "descripcion": c.descripcion,
                "activo": c.activo,
            }
            for c in categorias
        ])


    @app.route("/categorias-productos", methods=["POST"])
    def crear_categoria_producto():
        data = request.get_json()
        nombre = data.get("nombre")
        if not nombre:
            return jsonify({"error": "nombre es requerido"}), 400

        if CategoriaProducto.query.filter_by(nombre=nombre).first():
            return jsonify({"error": "ya existe una categoría con ese nombre"}), 400

        c = CategoriaProducto(
            nombre=nombre,
            descripcion=data.get("descripcion"),
            activo=data.get("activo", True),
        )
        db.session.add(c)
        db.session.commit()
        return jsonify({"id": c.id}), 201


    @app.route("/categorias-productos/<int:cat_id>", methods=["PUT", "PATCH"])
    def actualizar_categoria_producto(cat_id):
        c = CategoriaProducto.query.get_or_404(cat_id)
        data = request.get_json()

        if "nombre" in data:
            nuevo = data["nombre"]
            if nuevo != c.nombre and CategoriaProducto.query.filter_by(nombre=nuevo).first():
                return jsonify({"error": "ya existe una categoría con ese nombre"}), 400
            c.nombre = nuevo

        if "descripcion" in data:
            c.descripcion = data["descripcion"]

        if "activo" in data:
            c.activo = bool(data["activo"])

        db.session.commit()
        return jsonify({"message": "Categoría de producto actualizada"})


    @app.route("/categorias-productos/<int:cat_id>", methods=["DELETE"])
    def eliminar_categoria_producto(cat_id):
        c = CategoriaProducto.query.get_or_404(cat_id)
        db.session.delete(c)
        db.session.commit()
        return jsonify({"message": "Categoría de producto eliminada"})
    
    # ---------- CRUD CATEGORIAS SERVICIOS ----------

    @app.route("/categorias-servicios", methods=["GET"])
    def listar_categorias_servicios():
        categorias = CategoriaServicio.query.order_by(CategoriaServicio.nombre).all()
        return jsonify([
            {
                "id": c.id,
                "nombre": c.nombre,
                "descripcion": c.descripcion,
                "activo": c.activo,
            }
            for c in categorias
        ])


    @app.route("/categorias-servicios", methods=["POST"])
    def crear_categoria_servicio():
        data = request.get_json()
        nombre = data.get("nombre")
        if not nombre:
            return jsonify({"error": "nombre es requerido"}), 400

        if CategoriaServicio.query.filter_by(nombre=nombre).first():
            return jsonify({"error": "ya existe una categoría con ese nombre"}), 400

        c = CategoriaServicio(
            nombre=nombre,
            descripcion=data.get("descripcion"),
            activo=data.get("activo", True),
        )
        db.session.add(c)
        db.session.commit()
        return jsonify({"id": c.id}), 201


    @app.route("/categorias-servicios/<int:cat_id>", methods=["PUT", "PATCH"])
    def actualizar_categoria_servicio(cat_id):
        c = CategoriaServicio.query.get_or_404(cat_id)
        data = request.get_json()

        if "nombre" in data:
            nuevo = data["nombre"]
            if nuevo != c.nombre and CategoriaServicio.query.filter_by(nombre=nuevo).first():
                return jsonify({"error": "ya existe una categoría con ese nombre"}), 400
            c.nombre = nuevo

        if "descripcion" in data:
            c.descripcion = data["descripcion"]

        if "activo" in data:
            c.activo = bool(data["activo"])

        db.session.commit()
        return jsonify({"message": "Categoría de servicio actualizada"})


    @app.route("/categorias-servicios/<int:cat_id>", methods=["DELETE"])
    def eliminar_categoria_servicio(cat_id):
        c = CategoriaServicio.query.get_or_404(cat_id)
        db.session.delete(c)
        db.session.commit()
        return jsonify({"message": "Categoría de servicio eliminada"})


    # ---------- CRUD MARCAS PRODUCTOS ----------

    @app.route("/marcas-productos", methods=["GET"])
    def listar_marcas_productos():
        marcas = MarcaProducto.query.order_by(MarcaProducto.nombre).all()
        return jsonify([
            {
                "id": m.id,
                "nombre": m.nombre,
                "descripcion": m.descripcion,
                "activo": m.activo,
            }
            for m in marcas
        ])


    @app.route("/marcas-productos", methods=["POST"])
    def crear_marca_producto():
        data = request.get_json()
        nombre = data.get("nombre")
        if not nombre:
            return jsonify({"error": "nombre es requerido"}), 400

        if MarcaProducto.query.filter_by(nombre=nombre).first():
            return jsonify({"error": "ya existe una marca con ese nombre"}), 400

        m = MarcaProducto(
            nombre=nombre,
            descripcion=data.get("descripcion"),
            activo=data.get("activo", True),
        )
        db.session.add(m)
        db.session.commit()
        return jsonify({"id": m.id}), 201


    @app.route("/marcas-productos/<int:marca_id>", methods=["PUT", "PATCH"])
    def actualizar_marca_producto(marca_id):
        m = MarcaProducto.query.get_or_404(marca_id)
        data = request.get_json()

        if "nombre" in data:
            nuevo = data["nombre"]
            if nuevo != m.nombre and MarcaProducto.query.filter_by(nombre=nuevo).first():
                return jsonify({"error": "ya existe una marca con ese nombre"}), 400
            m.nombre = nuevo

        if "descripcion" in data:
            m.descripcion = data["descripcion"]

        if "activo" in data:
            m.activo = bool(data["activo"])

        db.session.commit()
        return jsonify({"message": "Marca de producto actualizada"})


    @app.route("/marcas-productos/<int:marca_id>", methods=["DELETE"])
    def eliminar_marca_producto(marca_id):
        m = MarcaProducto.query.get_or_404(marca_id)
        db.session.delete(m)
        db.session.commit()
        return jsonify({"message": "Marca de producto eliminada"})


    # =========================
    # CRUD CLIENTES
    # =========================

    @app.route("/clientes", methods=["GET"])
    def listar_clientes():
        """
        Lista todos los clientes.
        Opcional: ?q=texto para filtrar por nombre (para el Autocomplete).
        """
        q = request.args.get("q", type=str)

        query = Cliente.query
        if q:
            # filtra por nombre que contenga 'q' (case-insensitive)
            like = f"%{q}%"
            query = query.filter(Cliente.nombre.ilike(like))

        clientes = query.order_by(Cliente.nombre.asc()).all()

        return jsonify([
            {
                "id": c.id,
                "nombre": c.nombre,
                "telefono": c.telefono,
            }
            for c in clientes
        ]), 200


    @app.route("/clientes/<int:cliente_id>", methods=["GET"])
    def obtener_cliente(cliente_id):
        """
        Obtener un cliente por ID.
        """
        cliente = Cliente.query.get_or_404(cliente_id)
        return jsonify({
            "id": cliente.id,
            "nombre": cliente.nombre,
            "telefono": cliente.telefono,
        }), 200


    @app.route("/clientes", methods=["POST"])
    def crear_cliente():
        """
        Crear un nuevo cliente.
        Body JSON:
        {
        "nombre": "Ana López",
        "telefono": "+502 5555 1111"
        }
        """
        data = request.get_json() or {}

        nombre = data.get("nombre")
        telefono = data.get("telefono")

        if not nombre or not telefono:
            return jsonify({"error": "nombre y telefono son obligatorios"}), 400

        nuevo = Cliente(
            nombre=nombre.strip(),
            telefono=telefono.strip(),
        )
        db.session.add(nuevo)
        db.session.commit()

        return jsonify({
            "id": nuevo.id,
            "nombre": nuevo.nombre,
            "telefono": nuevo.telefono,
        }), 201


    @app.route("/clientes/<int:cliente_id>", methods=["PUT", "PATCH"])
    def actualizar_cliente(cliente_id):
        """
        Actualizar un cliente existente.
        Body JSON (campos opcionales):
        {
        "nombre": "Nuevo nombre",
        "telefono": "Nuevo teléfono"
        }
        """
        cliente = Cliente.query.get_or_404(cliente_id)
        data = request.get_json() or {}

        nombre = data.get("nombre")
        telefono = data.get("telefono")

        if nombre is not None:
            cliente.nombre = nombre.strip()

        if telefono is not None:
            cliente.telefono = telefono.strip()

        db.session.commit()

        return jsonify({
            "id": cliente.id,
            "nombre": cliente.nombre,
            "telefono": cliente.telefono,
        }), 200


    @app.route("/clientes/<int:cliente_id>", methods=["DELETE"])
    def eliminar_cliente(cliente_id):
        """
        Eliminar un cliente.
        Opcional: podrías evitar borrar si tiene órdenes asociadas.
        """
        cliente = Cliente.query.get_or_404(cliente_id)

        # Si quieres evitar borrar clientes con órdenes:
        # if cliente.ordenes and len(cliente.ordenes) > 0:
        #     return jsonify({"error": "No se puede eliminar un cliente con órdenes asociadas"}), 400

        db.session.delete(cliente)
        db.session.commit()

        return jsonify({"message": "Cliente eliminado correctamente"}), 200

    # =========================
    # CRUD EMPLEADAS
    # =========================

    @app.route("/empleadas", methods=["GET"])
    def listar_empleadas():
        """
        Lista todas las empleadas.
        Opcional:
        - ?solo_activas=true para filtrar
        - ?q=texto para buscar por nombre
        """
        q = request.args.get("q", type=str)
        solo_activas = request.args.get("solo_activas", "").lower() == "true"

        query = Empleada.query

        if q:
            like = f"%{q}%"
            query = query.filter(Empleada.nombre.ilike(like))

        if solo_activas:
            query = query.filter(Empleada.activo.is_(True))

        empleadas = query.order_by(Empleada.nombre.asc()).all()

        return jsonify([
            {
                "id": e.id,
                "nombre": e.nombre,
                "telefono": e.telefono,
                "activo": e.activo,
                "creado_en": e.creado_en.isoformat(),
            }
            for e in empleadas
        ]), 200


    @app.route("/empleadas/<int:empleada_id>", methods=["GET"])
    def obtener_empleada(empleada_id):
        """
        Obtener una empleada por ID.
        """
        empleada = Empleada.query.get_or_404(empleada_id)
        return jsonify({
            "id": empleada.id,
            "nombre": empleada.nombre,
            "telefono": empleada.telefono,
            "activo": empleada.activo,
            "creado_en": empleada.creado_en.isoformat(),
        }), 200


    @app.route("/empleadas", methods=["POST"])
    def crear_empleada():
        """
        Crear una nueva empleada.
        Body JSON:
        {
        "nombre": "Ana",
        "telefono": "+502 ...",   # opcional
        "activo": true            # opcional (default True)
        }
        """
        data = request.get_json() or {}

        nombre = data.get("nombre")
        telefono = data.get("telefono")
        activo = data.get("activo", True)

        if not nombre:
            return jsonify({"error": "nombre es obligatorio"}), 400

        nueva = Empleada(
        nombre=nombre.strip(),
        telefono=telefono.strip() if telefono else None,
        activo=bool(activo),
        )

        db.session.add(nueva)
        db.session.commit()

        return jsonify({
            "id": nueva.id,
            "nombre": nueva.nombre,
            "telefono": nueva.telefono,
            "activo": nueva.activo,
            "creado_en": nueva.creado_en.isoformat(),
        }), 201


    @app.route("/empleadas/<int:empleada_id>", methods=["PUT", "PATCH"])
    def actualizar_empleada(empleada_id):
        """
        Actualizar una empleada existente.
        Body JSON (campos opcionales):
        {
        "nombre": "Nuevo nombre",
        "telefono": "Nuevo teléfono o null",
        "activo": false
        }
        """
        empleada = Empleada.query.get_or_404(empleada_id)
        data = request.get_json() or {}

        if "nombre" in data and data["nombre"] is not None:
            empleada.nombre = data["nombre"].strip()

        # teléfono puede ser string o null para limpiar
        if "telefono" in data:
            tel = data["telefono"]
            empleada.telefono = tel.strip() if tel else None

        if "activo" in data:
            empleada.activo = bool(data["activo"])

        db.session.commit()

        return jsonify({
            "id": empleada.id,
            "nombre": empleada.nombre,
            "telefono": empleada.telefono,
            "activo": empleada.activo,
            "creado_en": empleada.creado_en.isoformat(),
        }), 200


    @app.route("/empleadas/<int:empleada_id>", methods=["DELETE"])
    def eliminar_empleada(empleada_id):
        """
        Eliminar una empleada.
        Opcional: en vez de borrar, podrías solo marcar activo=False.
        """
        empleada = Empleada.query.get_or_404(empleada_id)

        # Si prefieres "baja lógica" en lugar de delete:
        # empleada.activo = False
        # db.session.commit()
        # return jsonify({"message": "Empleada desactivada"}), 200

        db.session.delete(empleada)
        db.session.commit()

        return jsonify({"message": "Empleada eliminada correctamente"}), 200

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)
