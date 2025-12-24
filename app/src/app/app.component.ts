import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';

interface OptimizeBody {
  [key: string]: number | Record<string, number>;
}

interface OptimizeResponse {
  solar_capacity: number;
  battery_capacity: number;
  off_peak_grid_usage: number;
  peak_grid_consumption: number;
}

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss'
})
export class AppComponent {
  title = 'energy-optimizer';
  
  // Form values
  peakPrice: number = 0.5;
  offPeakPrice: number = 0.4;
  batteryCostPerKw: number = 0.15;
  peakConsumption: number = 10;
  offPeakConsumption: number = 20;
  solarInstallationSizes: string = '{"3":0.282,"5":0.25,"6":0.23,"8":0.21,"10":0.19,"12":0.117}';
  
  result: string = 'No run yet.';
  isRunning: boolean = false;

  async onSubmit(): Promise<void> {
    const body: OptimizeBody = {
      peak_price: this.peakPrice,
      off_peak_price: this.offPeakPrice,
      battery_cost_per_kw: this.batteryCostPerKw,
      peak_consumption: this.peakConsumption,
      off_peak_consumption: this.offPeakConsumption,
    };

    try {
      body['solar_installation_sizes'] = JSON.parse(this.solarInstallationSizes);
    } catch (err) {
      this.result = 'Invalid JSON for solar sizes';
      return;
    }

    this.result = 'Running...';
    this.isRunning = true;

    try {
      const resp = await fetch('/optimize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(body),
      });
      const j = (await resp.json()) as OptimizeResponse;
      this.result = JSON.stringify(j, null, 2);
    } catch (err) {
      this.result = 'Request failed: ' + (err instanceof Error ? err.message : String(err));
    } finally {
      this.isRunning = false;
    }
  }
}
