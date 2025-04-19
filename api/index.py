from flask import Flask, request, jsonify

app = Flask(__name__)

# Warehouse data
warehouses = {
    'C1': {'A': 3, 'B': 2, 'C': 8, 'distance': 4},
    'C2': {'D': 12, 'E': 25, 'F': 15, 'distance': 3},
    'C3': {'G': 0.5, 'H': 1, 'I': 2, 'distance': 2}
}

def calculate_cost_per_unit(weight):
    if weight <= 5:
        return 10
    else:
        additional = weight - 5
        additional_blocks = (additional + 4) // 5
        return 10 + additional_blocks * 8

def calculate_path_cost(path, order):
    total_cost = 0
    current_weight = 0
    current_location = path[0]
    
    for i in range(1, len(path)):
        next_location = path[i]
        
        if current_location == 'L1':
            distance = warehouses[next_location]['distance']
        elif next_location == 'L1':
            distance = warehouses[current_location]['distance']
        else:
            distance = warehouses[current_location]['distance'] + warehouses[next_location]['distance']
        
        if current_location in warehouses:
            for product, quantity in order.items():
                if product in warehouses[current_location]:
                    current_weight += quantity * warehouses[current_location][product]
        
        cost_per_unit = calculate_cost_per_unit(current_weight)
        segment_cost = distance * cost_per_unit
        total_cost += segment_cost
        
        current_location = next_location
    
    return total_cost

def generate_possible_paths(order):
    paths = []
    centers_needed = set()
    
    for product in order:
        for center, products in warehouses.items():
            if product in products:
                centers_needed.add(center)
                break
    
    centers_needed = list(centers_needed)
    
    for start_center in ['C1', 'C2', 'C3']:
        other_centers = [c for c in centers_needed if c != start_center]
        
        from itertools import permutations
        for perm in permutations(other_centers):
            path = [start_center, 'L1']
            for center in perm:
                path.append(center)
                path.append('L1')
            paths.append(path)
        
        if len(other_centers) > 0:
            path = [start_center]
            for center in other_centers:
                path.append(center)
            path.append('L1')
            paths.append(path)
    
    return paths

@app.route('/api/calculate-delivery-cost', methods=['POST'])
def calculate_delivery_cost():
    try:
        order = request.get_json()
        if not order:
            return jsonify({'error': 'No order data provided'}), 400
        
        for product, quantity in order.items():
            if not isinstance(quantity, int) or quantity < 0:
                return jsonify({'error': f'Invalid quantity for product {product}'}), 400
            found = False
            for center in warehouses.values():
                if product in center:
                    found = True
                    break
            if not found:
                return jsonify({'error': f'Product {product} not found in any warehouse'}), 400
        
        paths = generate_possible_paths(order)
        
        min_cost = float('inf')
        best_path = None
        
        for path in paths:
            cost = calculate_path_cost(path, order)
            if cost < min_cost:
                min_cost = cost
                best_path = path
        
        return jsonify({'minimum_cost': min_cost, 'optimal_path': best_path})
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)
