import 'package:flutter/material.dart';
import 'package:provider/provider.dart';

import '../providers/auth_provider.dart';
import '../providers/trending_provider.dart';

class TrendingScreen extends StatelessWidget {
  const TrendingScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('热点监控'),
        actions: [
          Consumer<AuthProvider>(
            builder: (context, auth, _) {
              return Padding(
                padding: const EdgeInsets.only(right: 16),
                child: Chip(
                  avatar: Icon(
                    auth.isVip ? Icons.star : Icons.star_border,
                    color: auth.isVip ? Colors.amber : Colors.grey,
                    size: 18,
                  ),
                  label: Text(auth.isVip ? 'VIP' : '免费'),
                  backgroundColor: auth.isVip 
                      ? Colors.amber.withOpacity(0.2) 
                      : Colors.grey.withOpacity(0.2),
                ),
              );
            },
          ),
        ],
      ),
      body: Column(
        children: [
          // Platform Filter
          Consumer<TrendingProvider>(
            builder: (context, provider, _) {
              return SizedBox(
                height: 50,
                child: ListView(
                  scrollDirection: Axis.horizontal,
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  children: [
                    _buildPlatformChip(context, provider, null, '全部'),
                    ...provider.platforms.map((platform) => _buildPlatformChip(
                      context, 
                      provider, 
                      platform['id'],
                      platform['name'],
                    )),
                  ],
                ),
              );
            },
          ),
          
          // Content
          Expanded(
            child: Consumer<TrendingProvider>(
              builder: (context, provider, _) {
                if (provider.isLoading) {
                  return const Center(child: CircularProgressIndicator());
                }

                if (provider.error != null) {
                  return Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Text(provider.error!),
                        const SizedBox(height: 16),
                        ElevatedButton(
                          onPressed: () => provider.refresh(),
                          child: const Text('重试'),
                        ),
                      ],
                    ),
                  );
                }

                if (provider.trendingData.isEmpty) {
                  return const Center(
                    child: Text('暂无数据'),
                  );
                }

                return RefreshIndicator(
                  onRefresh: () => provider.refresh(),
                  child: ListView.builder(
                    padding: const EdgeInsets.all(16),
                    itemCount: provider.trendingData.length,
                    itemBuilder: (context, index) {
                      final platform = provider.trendingData[index];
                      return _buildPlatformCard(context, platform);
                    },
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildPlatformChip(
    BuildContext context, 
    TrendingProvider provider, 
    String? platformId,
    String label,
  ) {
    final isSelected = provider.selectedPlatform == platformId;
    
    return Padding(
      padding: const EdgeInsets.only(right: 8),
      child: FilterChip(
        label: Text(label),
        selected: isSelected,
        onSelected: (_) => provider.selectPlatform(platformId),
      ),
    );
  }

  Widget _buildPlatformCard(BuildContext context, dynamic platform) {
    final items = platform['data'] as List? ?? [];
    
    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Header
          Padding(
            padding: const EdgeInsets.all(16),
            child: Row(
              children: [
                const Icon(Icons.hot_tub, color: Colors.red),
                const SizedBox(width: 8),
                Text(
                  platform['platform'] ?? '',
                  style: const TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.bold,
                  ),
                ),
                const Spacer(),
                Text(
                  _formatTime(platform['updated_at']),
                  style: const TextStyle(
                    color: Colors.grey,
                    fontSize: 12,
                  ),
                ),
              ],
            ),
          ),
          
          const Divider(height: 1),
          
          // Items
          ListView.separated(
            shrinkWrap: true,
            physics: const NeverScrollableScrollPhysics(),
            itemCount: items.length > 10 ? 10 : items.length,
            separatorBuilder: (_, __) => const Divider(height: 1),
            itemBuilder: (context, index) {
              final item = items[index];
              return ListTile(
                leading: CircleAvatar(
                  backgroundColor: index < 3 ? Colors.red : Colors.grey[300],
                  foregroundColor: index < 3 ? Colors.white : Colors.grey[600],
                  radius: 14,
                  child: Text(
                    '${item['rank'] ?? index + 1}',
                    style: const TextStyle(fontSize: 12),
                  ),
                ),
                title: Text(
                  item['title'] ?? '',
                  maxLines: 2,
                  overflow: TextOverflow.ellipsis,
                ),
                subtitle: item['hot_value'] != null
                    ? Text(
                        '热度: ${item['hot_value']}',
                        style: const TextStyle(color: Colors.orange),
                      )
                    : null,
              );
            },
          ),
        ],
      ),
    );
  }

  String _formatTime(String? timeStr) {
    if (timeStr == null) return '';
    try {
      final dt = DateTime.parse(timeStr);
      return '${dt.hour}:${dt.minute.toString().padLeft(2, '0')}';
    } catch (e) {
      return '';
    }
  }
}
