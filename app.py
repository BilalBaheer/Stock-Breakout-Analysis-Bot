from flask import Flask, render_template, request, jsonify, send_file, send_from_directory
from utils.stock_analysis import analyze_stock_breakout
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

# Add a route for static files
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        print(f"Received request with data: {data}")
        
        ticker = data['ticker'].upper()
        start_date = data['startDate']
        end_date = data['endDate']
        volume_threshold = float(data['volumeThreshold'])
        price_threshold = float(data['priceThreshold'])
        holding_period = int(data['holdingPeriod'])
        
        print(f"Processing analysis for {ticker} from {start_date} to {end_date}")
        print(f"Parameters: Volume threshold={volume_threshold}%, Price threshold={price_threshold}%, Holding period={holding_period} days")

        # Analyze the stock
        results = analyze_stock_breakout(
            ticker, 
            start_date, 
            end_date, 
            volume_threshold, 
            price_threshold, 
            holding_period
        )

        if results is None:
            return jsonify({
                'error': 'No data found. Please check if:\n' +
                        '1. The date range is valid\n' +
                        '2. The stock ticker is correct\n' +
                        'Note: We are mapping your dates to 2022 for historical analysis.\n' +
                        'For example: 2024-01-01 is mapped to 2022-01-01'
            }), 400

        if len(results) == 0:
            return jsonify({
                'error': 'No breakout events found.\n' +
                        'Try adjusting your parameters:\n' +
                        '1. Decrease the volume threshold (currently ' + str(volume_threshold) + '%)\n' +
                        '2. Decrease the price threshold (currently ' + str(price_threshold) + '%)\n' +
                        '3. Extend the date range'
            }), 400

        # Save results to CSV
        csv_filename = f'breakout_analysis_{ticker}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv'
        results.to_csv(f'static/{csv_filename}', index=True)

        return jsonify({
            'success': True,
            'message': 'Analysis completed successfully',
            'csv_url': f'/static/{csv_filename}'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False)
