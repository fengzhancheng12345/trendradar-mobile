import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../providers/auth_provider.dart';
import '../providers/vip_provider.dart';

class VipScreen extends StatelessWidget {
  const VipScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('VIP会员'),
      ),
      body: Consumer2<VipProvider, AuthProvider>(
        builder: (context, vipProvider, authProvider, _) {
          if (vipProvider.isVip) {
            return _buildVipActive(context, vipProvider);
          }
          return _buildVipUpgrade(context, vipProvider, authProvider);
        },
      ),
    );
  }

  Widget _buildVipActive(BuildContext context, VipProvider provider) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        children: [
          const SizedBox(height: 40),
          
          // VIP Badge
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Color(0xFFFFD700), Color(0xFFFFA500)],
              ),
              borderRadius: BorderRadius.circular(16),
            ),
            child: const Column(
              children: [
                Icon(Icons.star, size: 60, color: Colors.white),
                SizedBox(height: 16),
                Text(
                  'VIP会员',
                  style: TextStyle(
                    fontSize: 28,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                SizedBox(height: 8),
                Text(
                  '有效期至: 2026-12-31',
                  style: TextStyle(color: Colors.white70),
                ),
              ],
            ),
          ),
          
          const SizedBox(height: 32),
          
          // VIP Features
          const Text(
            '您已享有的VIP特权',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 16),
          
          _buildFeatureItem(Icons.speed, '5分钟更新频率', '实时掌握热点动态'),
          _buildFeatureItem(Icons.apps, '20+平台监控', '覆盖全网热点'),
          _buildFeatureItem(Icons.psychology, 'AI智能分析', '深度洞察趋势'),
          _buildFeatureItem(Icons.history, '30天历史数据', '回顾历史热点'),
          _buildFeatureItem(Icons.label, '10个关键词', '精准追踪关注'),
        ],
      ),
    );
  }

  Widget _buildVipUpgrade(BuildContext context, VipProvider provider, AuthProvider auth) {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(24),
      child: Column(
        children: [
          const SizedBox(height: 24),
          
          // Banner
          Container(
            padding: const EdgeInsets.all(24),
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [Color(0xFF1677FF), Color(0xFF4096FF)],
              ),
              borderRadius: BorderRadius.circular(16),
            ),
            child: Column(
              children: [
                const Icon(Icons.qr_code, size: 60, color: Colors.white),
                const SizedBox(height: 16),
                const Text(
                  '支付宝当面付',
                  style: TextStyle(
                    fontSize: 28,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                ),
                const SizedBox(height: 8),
                const Text(
                  '扫码支付，快速开通VIP',
                  style: TextStyle(color: Colors.white70),
                ),
                const SizedBox(height: 16),
                
                // Current Status
                Container(
                  padding: const EdgeInsets.all(12),
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Column(
                    children: [
                      const Row(
                        mainAxisAlignment: MainAxisAlignment.spaceAround,
                        children: [
                          _StatItem(value: '30分钟', label: '更新频率'),
                          _StatItem(value: '11', label: '平台数量'),
                          _StatItem(value: '1', label: '关键词'),
                        ],
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),
          
          const SizedBox(height: 32),
          
          // Products
          const Text(
            '选择套餐',
            style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
          ),
          const SizedBox(height: 16),
          
          ...provider.products.map<Widget>((product) => _buildProductCard(
            context, 
            provider, 
            product,
          )),
        ],
      ),
    );
  }

  Widget _buildProductCard(BuildContext context, VipProvider provider, dynamic product) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        contentPadding: const EdgeInsets.all(16),
        title: Text(
          product['description'] ?? '',
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: const Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            SizedBox(height: 4),
            Text('• 5分钟更新频率'),
            Text('• 20+平台监控'),
            Text('• AI智能分析'),
            Text('• 30天历史数据'),
            Text('• 10个关键词'),
          ],
        ),
        trailing: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            Text(
              '¥${product['price']}',
              style: const TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: Color(0xFF1677FF),
              ),
            ),
            if (product['duration_days'] == 365)
              const Text(
                '省40%',
                style: TextStyle(color: Colors.red, fontSize: 12),
              ),
          ],
        ),
        onTap: () => _showPayDialog(context, provider, product),
      ),
    );
  }

  void _showPayDialog(BuildContext context, VipProvider provider, dynamic product) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (context) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              const Text(
                '支付宝当面付',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
              ),
              const SizedBox(height: 8),
              const Text(
                '扫码支付，快速开通VIP',
                style: TextStyle(color: Colors.grey),
              ),
              const SizedBox(height: 24),
              
              // Pay Button
              SizedBox(
                width: double.infinity,
                child: ElevatedButton.icon(
                  onPressed: provider.isLoading 
                      ? null 
                      : () async {
                          final result = await provider.createOrder(
                            product['duration_days'],
                            'alipay',
                          );
                          if (result != null && context.mounted) {
                            Navigator.pop(context);
                            _showQrCodeDialog(context, provider, result);
                          }
                        },
                  icon: const Icon(Icons.qr_code),
                  label: const Text('生成收款码'),
                  style: ElevatedButton.styleFrom(
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    backgroundColor: const Color(0xFF1677FF),
                  ),
                ),
              ),
              
              const SizedBox(height: 16),
              
              // Instructions
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: Colors.grey[100],
                  borderRadius: BorderRadius.circular(8),
                ),
                child: const Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      '支付步骤:',
                      style: TextStyle(fontWeight: FontWeight.bold),
                    ),
                    SizedBox(height: 4),
                    Text('1. 点击"生成收款码"'),
                    Text('2. 使用支付宝扫码支付'),
                    Text('3. 支付完成后自动开通VIP'),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _showQrCodeDialog(BuildContext context, VipProvider provider, Map<String, dynamic> orderData) {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => _PayDialog(
        orderNo: orderData['order_no'] ?? '',
        amount: orderData['amount']?.toDouble() ?? 0,
        qrCodeImage: orderData['qr_code_image'] ?? '',
        onCheckPayment: () async {
          return await provider.checkPayment(orderData['order_no'] ?? '');
        },
        onSuccess: () {
          Navigator.pop(context);
          Navigator.pop(context);
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(
              content: Text('VIP开通成功！'),
              backgroundColor: Colors.green,
            ),
          );
        },
      ),
    );
  }

  Widget _buildFeatureItem(IconData icon, String title, String desc) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          Container(
            padding: const EdgeInsets.all(8),
            decoration: BoxDecoration(
              color: const Color(0xFF1677FF).withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
            ),
            child: Icon(icon, color: const Color(0xFF1677FF)),
          ),
          const SizedBox(width: 16),
          Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(title, style: const TextStyle(fontWeight: FontWeight.bold)),
              Text(desc, style: const TextStyle(color: Colors.grey, fontSize: 12)),
            ],
          ),
        ],
      ),
    );
  }
}

class _StatItem extends StatelessWidget {
  final String value;
  final String label;

  const _StatItem({required this.value, required this.label});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(
          value,
          style: const TextStyle(
            color: Colors.white,
            fontSize: 18,
            fontWeight: FontWeight.bold,
          ),
        ),
        Text(
          label,
          style: const TextStyle(color: Colors.white70, fontSize: 12),
        ),
      ],
    );
  }
}

// 支付弹窗
class _PayDialog extends StatefulWidget {
  final String orderNo;
  final double amount;
  final String qrCodeImage;
  final Future<bool> Function() onCheckPayment;
  final VoidCallback onSuccess;

  const _PayDialog({
    required this.orderNo,
    required this.amount,
    required this.qrCodeImage,
    required this.onCheckPayment,
    required this.onSuccess,
  });

  @override
  State<_PayDialog> createState() => _PayDialogState();
}

class _PayDialogState extends State<_PayDialog> {
  bool _isPolling = false;
  int _countdown = 60;

  @override
  void initState() {
    super.initState();
    _startPolling();
  }

  void _startPolling() {
    _isPolling = true;
    _pollPayment();
  }

  Future<void> _pollPayment() async {
    while (_isPolling && _countdown > 0) {
      await Future.delayed(const Duration(seconds: 2));
      _countdown -= 2;
      
      if (!mounted) return;
      
      final success = await widget.onCheckPayment();
      if (success) {
        widget.onSuccess();
        return;
      }
      
      setState(() {});
    }
    
    if (_countdown <= 0 && mounted) {
      Navigator.pop(context);
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('支付超时，请重新发起')),
      );
    }
  }

  @override
  void dispose() {
    _isPolling = false;
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return AlertDialog(
      title: const Text('请扫码支付'),
      content: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          // QR Code
          if (widget.qrCodeImage.isNotEmpty)
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Image.network(
                widget.qrCodeImage,
                width: 200,
                height: 200,
                errorBuilder: (_, __, ___) => const Icon(
                  Icons.qr_code_2,
                  size: 200,
                  color: Colors.grey,
                ),
              ),
            ),
          
          const SizedBox(height: 16),
          
          // Amount
          Text(
            '¥${widget.amount.toStringAsFixed(2)}',
            style: const TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: Color(0xFF1677FF),
            ),
          ),
          
          const SizedBox(height: 8),
          
          // Countdown
          Text(
            '请在 ${_countdown} 秒内完成支付',
            style: TextStyle(color: Colors.grey[600]),
          ),
          
          const SizedBox(height: 16),
          
          // Loading
          const LinearProgressIndicator(),
        ],
      ),
      actions: [
        TextButton(
          onPressed: () => Navigator.pop(context),
          child: const Text('取消'),
        ),
      ],
    );
  }
}
